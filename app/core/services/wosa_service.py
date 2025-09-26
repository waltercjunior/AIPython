"""
Services for WOSA Reports processing.
"""
import json
import base64
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.infrastructure.database.wosa_models import (
    File, ApplicationComponent, InterfaceType, Interface, Topic,
    TopicProducer, TopicConsumer, MissingProducer, MissingConsumer,
    TopicHistory, Report, ReportItem
)
from app.schemas.wosa_schemas import (
    WOSAReportData, FileUploadRequest, ProcessingResult,
    TopicData, TopicObject, TopicStats
)
from app.exceptions import ValidationError, NotFoundError, ConflictError


class WOSAFileService:
    """Service for handling WOSA file operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def upload_file(self, request: FileUploadRequest) -> File:
        """Upload and process a WOSA JSON file."""
        
        # Validate JSON content
        try:
            json_content = base64.b64decode(request.content).decode('utf-8')
            wosa_data = WOSAReportData.parse_raw(json_content)
        except Exception as e:
            raise ValidationError(f"Invalid JSON format: {str(e)}")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"{request.filename.lower()} {timestamp}"
        
        # Check if filename already exists
        existing_file = self.db.query(File).filter(File.name == filename).first()
        if existing_file:
            raise ConflictError(f"File with name '{filename}' already exists")
        
        # Create file record
        file_record = File(
            name=filename,
            original_name=request.filename,
            user_id=request.user_id,
            file_size=len(json_content),
            status="pending"
        )
        
        self.db.add(file_record)
        self.db.commit()
        self.db.refresh(file_record)
        
        return file_record
    
    async def process_file(self, file_id: int) -> ProcessingResult:
        """Process a WOSA file and extract topics."""
        
        file_record = self.db.query(File).filter(File.id == file_id).first()
        if not file_record:
            raise NotFoundError(f"File with ID {file_id} not found")
        
        # Update file status
        file_record.status = "processing"
        file_record.processing_date = datetime.utcnow()
        self.db.commit()
        
        try:
            # Get the JSON content (in real implementation, you'd read from file)
            # For now, we'll assume the data is available
            result = ProcessingResult(
                file_id=file_id,
                status="processing",
                topics_processed=0,
                topics_created=0,
                topics_updated=0,
                errors=[],
                warnings=[]
            )
            
            # Update file status to completed
            file_record.status = "completed"
            self.db.commit()
            
            result.status = "completed"
            return result
            
        except Exception as e:
            file_record.status = "error"
            self.db.commit()
            raise ValidationError(f"Error processing file: {str(e)}")


class WOSATopicService:
    """Service for handling WOSA topic operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def process_topics(self, file_id: int, topics_data: List[TopicData]) -> ProcessingResult:
        """Process topics from WOSA data."""
        
        result = ProcessingResult(
            file_id=file_id,
            status="processing",
            topics_processed=len(topics_data),
            topics_created=0,
            topics_updated=0,
            errors=[],
            warnings=[]
        )
        
        for topic_data in topics_data:
            try:
                # Extract topic object data
                topic_object = topic_data.object
                
                # Check if topic already exists
                existing_topic = self.db.query(Topic).filter(
                    Topic.name == topic_object.name
                ).first()
                
                if existing_topic:
                    # Update existing topic
                    await self._update_topic(existing_topic, topic_object, file_id)
                    result.topics_updated += 1
                else:
                    # Create new topic
                    await self._create_topic(topic_object, file_id)
                    result.topics_created += 1
                    
            except Exception as e:
                result.errors.append(f"Error processing topic {topic_data.name}: {str(e)}")
        
        result.status = "completed"
        return result
    
    async def _create_topic(self, topic_object: TopicObject, file_id: int) -> Topic:
        """Create a new topic."""
        
        topic = Topic(
            name=topic_object.name,
            file_id=file_id,
            bridged_topic=topic_object.bridged_topic,
            environment=self._detect_environment(topic_object.name),
            **topic_object.stats.dict()
        )
        
        self.db.add(topic)
        self.db.commit()
        self.db.refresh(topic)
        
        # Create producers
        for producer_name in topic_object.producers:
            producer = TopicProducer(
                topic_id=topic.id,
                producer_name=producer_name
            )
            self.db.add(producer)
        
        # Create consumers
        for consumer_name in topic_object.consumers:
            consumer = TopicConsumer(
                topic_id=topic.id,
                consumer_name=consumer_name
            )
            self.db.add(consumer)
        
        # Create missing producers
        for producer_name in topic_object.missing_producers:
            missing_producer = MissingProducer(
                topic_id=topic.id,
                producer_name=producer_name
            )
            self.db.add(missing_producer)
        
        # Create missing consumers
        for consumer_name in topic_object.missing_consumers:
            missing_consumer = MissingConsumer(
                topic_id=topic.id,
                consumer_name=consumer_name
            )
            self.db.add(missing_consumer)
        
        # Create history record
        history = TopicHistory(
            topic_id=topic.id,
            file_id=file_id,
            action="created",
            changes={"name": topic_object.name}
        )
        self.db.add(history)
        
        self.db.commit()
        return topic
    
    async def _update_topic(self, topic: Topic, topic_object: TopicObject, file_id: int) -> Topic:
        """Update an existing topic."""
        
        # Track changes
        changes = {}
        
        # Update basic fields
        if topic.bridged_topic != topic_object.bridged_topic:
            changes["bridged_topic"] = topic_object.bridged_topic
            topic.bridged_topic = topic_object.bridged_topic
        
        # Update stats
        stats_dict = topic_object.stats.dict()
        for field, value in stats_dict.items():
            if getattr(topic, field) != value:
                changes[field] = value
                setattr(topic, field, value)
        
        # Update last seen
        topic.last_seen = datetime.utcnow()
        
        # Update producers, consumers, etc. (simplified for now)
        self.db.commit()
        
        # Create history record
        if changes:
            history = TopicHistory(
                topic_id=topic.id,
                file_id=file_id,
                action="updated",
                changes=changes
            )
            self.db.add(history)
            self.db.commit()
        
        return topic
    
    def _detect_environment(self, topic_name: str) -> Optional[str]:
        """Detect environment from topic name."""
        topic_name_lower = topic_name.lower()
        
        if any(env in topic_name_lower for env in ['dev', 'development']):
            return 'dev'
        elif any(env in topic_name_lower for env in ['prod', 'production']):
            return 'prod'
        elif any(env in topic_name_lower for env in ['e2e', 'test']):
            return 'e2e'
        
        return None


class WOSAReportService:
    """Service for generating WOSA reports."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_report(self, report_type: int, parameters: Optional[Dict] = None) -> Report:
        """Generate a WOSA report."""
        
        if report_type < 1 or report_type > 10:
            raise ValidationError("Report type must be between 1 and 10")
        
        # Generate report based on type
        report_data = await self._get_report_data(report_type, parameters)
        
        # Create report record
        report = Report(
            report_type=report_type,
            report_name=f"WOSA Report {report_type}",
            generated_by=parameters.get("generated_by") if parameters else None,
            parameters=parameters,
            results_count=len(report_data)
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        # Create report items
        for item_data in report_data:
            report_item = ReportItem(
                report_id=report.id,
                topic_id=item_data.get("topic_id"),
                item_data=item_data
            )
            self.db.add(report_item)
        
        self.db.commit()
        return report
    
    async def _get_report_data(self, report_type: int, parameters: Optional[Dict]) -> List[Dict]:
        """Get data for specific report type."""
        
        if report_type == 1:
            return await self._get_topics_without_producers()
        elif report_type == 2:
            return await self._get_topics_without_consumers()
        elif report_type == 3:
            return await self._get_topics_30_days_no_message()
        elif report_type == 4:
            return await self._get_topics_60_days_no_message()
        elif report_type == 5:
            return await self._get_topics_90_days_no_message()
        elif report_type == 6:
            return await self._get_topics_multiple_producers()
        elif report_type == 7:
            return await self._get_topics_no_ac_registered()
        elif report_type == 8:
            return await self._get_topics_not_documented()
        elif report_type == 9:
            return await self._get_topics_modified_30_60_90_days()
        elif report_type == 10:
            return await self._get_topics_wrong_environment()
        
        return []
    
    async def _get_topics_without_producers(self) -> List[Dict]:
        """Report 1: Topics without producers."""
        topics = self.db.query(Topic).outerjoin(TopicProducer).filter(
            TopicProducer.id.is_(None)
        ).all()
        
        return [{"topic_id": t.id, "topic_name": t.name, "reason": "No producers"} for t in topics]
    
    async def _get_topics_without_consumers(self) -> List[Dict]:
        """Report 2: Topics without consumers."""
        topics = self.db.query(Topic).outerjoin(TopicConsumer).filter(
            TopicConsumer.id.is_(None)
        ).all()
        
        return [{"topic_id": t.id, "topic_name": t.name, "reason": "No consumers"} for t in topics]
    
    async def _get_topics_30_days_no_message(self) -> List[Dict]:
        """Report 3: Topics with more than 30 days without message."""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        topics = self.db.query(Topic).filter(
            or_(
                Topic.last_message_date.is_(None),
                Topic.last_message_date < thirty_days_ago
            )
        ).all()
        
        return [{"topic_id": t.id, "topic_name": t.name, "last_message": t.last_message_date} for t in topics]
    
    async def _get_topics_60_days_no_message(self) -> List[Dict]:
        """Report 4: Topics with more than 60 days without message."""
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)
        
        topics = self.db.query(Topic).filter(
            or_(
                Topic.last_message_date.is_(None),
                Topic.last_message_date < sixty_days_ago
            )
        ).all()
        
        return [{"topic_id": t.id, "topic_name": t.name, "last_message": t.last_message_date} for t in topics]
    
    async def _get_topics_90_days_no_message(self) -> List[Dict]:
        """Report 5: Topics with more than 90 days without message."""
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        
        topics = self.db.query(Topic).filter(
            or_(
                Topic.last_message_date.is_(None),
                Topic.last_message_date < ninety_days_ago
            )
        ).all()
        
        return [{"topic_id": t.id, "topic_name": t.name, "last_message": t.last_message_date} for t in topics]
    
    async def _get_topics_multiple_producers(self) -> List[Dict]:
        """Report 6: Topics with multiple producers."""
        # This would require a more complex query to count producers per topic
        return []
    
    async def _get_topics_no_ac_registered(self) -> List[Dict]:
        """Report 7: Topics without AC registered in Vlad Producer/Consumer."""
        topics = self.db.query(Topic).filter(
            Topic.interface_id.is_(None)
        ).all()
        
        return [{"topic_id": t.id, "topic_name": t.name, "reason": "No AC registered"} for t in topics]
    
    async def _get_topics_not_documented(self) -> List[Dict]:
        """Report 8: Topics not documented."""
        # This would require additional documentation tracking
        return []
    
    async def _get_topics_modified_30_60_90_days(self) -> List[Dict]:
        """Report 9: Topics modified in last 30/60/90 days."""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        topics = self.db.query(Topic).filter(
            Topic.updated_at > thirty_days_ago
        ).all()
        
        return [{"topic_id": t.id, "topic_name": t.name, "updated_at": t.updated_at} for t in topics]
    
    async def _get_topics_wrong_environment(self) -> List[Dict]:
        """Report 10: Topics with wrong environment."""
        topics = self.db.query(Topic).filter(
            Topic.environment.notin_(['dev', 'prod', 'e2e'])
        ).all()
        
        return [{"topic_id": t.id, "topic_name": t.name, "environment": t.environment} for t in topics]


class IDGenerationService:
    """Service for generating unique IDs."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_next_available_id(self, entity: str, requested_id: int) -> Dict[str, Any]:
        """Get next available ID for an entity."""
        
        # Map entity names to model classes
        entity_map = {
            "file": File,
            "application_component": ApplicationComponent,
            "interface_type": InterfaceType,
            "interface": Interface,
            "topic": Topic,
            "report": Report
        }
        
        if entity not in entity_map:
            raise ValidationError(f"Unknown entity: {entity}")
        
        model_class = entity_map[entity]
        
        # Check if requested ID is available
        existing_record = self.db.query(model_class).filter(
            model_class.id == requested_id
        ).first()
        
        if not existing_record:
            return {
                "entity": entity,
                "requested_id": requested_id,
                "available_id": requested_id,
                "is_available": True
            }
        
        # Find next available ID
        max_id = self.db.query(func.max(model_class.id)).scalar() or 0
        next_id = max_id + 1
        
        return {
            "entity": entity,
            "requested_id": requested_id,
            "available_id": next_id,
            "is_available": False
        }
