"""
API routes for WOSA Reports system.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
import json

from app.database import get_db
from app.infrastructure.database.wosa_models import (
    File, ApplicationComponent, InterfaceType, Interface, Topic,
    TopicProducer, TopicConsumer, MissingProducer, MissingConsumer
)
from app.schemas.wosa_schemas import (
    FileUploadRequest, FileResponse, ProcessingResult,
    ApplicationComponentCreate, ApplicationComponentResponse,
    InterfaceTypeCreate, InterfaceTypeResponse,
    InterfaceCreate, InterfaceResponse,
    TopicResponse, TopicDetailResponse,
    ReportRequest, ReportResponse,
    IDGenerationRequest, IDGenerationResponse
)
from app.core.services.wosa_service import (
    WOSAFileService, WOSATopicService, WOSAReportService, IDGenerationService
)
from app.exceptions import BaseAPIException

router = APIRouter()


@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_wosa_file(
    file: UploadFile = File(...),
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Upload a WOSA JSON file for processing."""
    try:
        # Read file content
        content = await file.read()
        content_b64 = base64.b64encode(content).decode('utf-8')
        
        # Create upload request
        upload_request = FileUploadRequest(
            filename=file.filename,
            user_id=user_id,
            content=content_b64
        )
        
        # Process file
        file_service = WOSAFileService(db)
        file_record = await file_service.upload_file(upload_request)
        
        return FileResponse.from_orm(file_record)
        
    except BaseAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.post("/process/{file_id}", response_model=ProcessingResult)
async def process_wosa_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    """Process a uploaded WOSA file."""
    try:
        file_service = WOSAFileService(db)
        result = await file_service.process_file(file_id)
        
        return result
        
    except BaseAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/files", response_model=List[FileResponse])
async def get_files(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of uploaded files."""
    files = db.query(File).offset(skip).limit(limit).all()
    return [FileResponse.from_orm(file) for file in files]


@router.get("/files/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific file by ID."""
    file_record = db.query(File).filter(File.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse.from_orm(file_record)


# Application Components endpoints
@router.post("/application-components", response_model=ApplicationComponentResponse, status_code=status.HTTP_201_CREATED)
async def create_application_component(
    component_data: ApplicationComponentCreate,
    db: Session = Depends(get_db)
):
    """Create a new application component."""
    try:
        # Check if component already exists
        existing = db.query(ApplicationComponent).filter(
            ApplicationComponent.name == component_data.name
        ).first()
        
        if existing:
            raise HTTPException(status_code=409, detail="Application component already exists")
        
        # Create new component
        component = ApplicationComponent(
            name=component_data.name,
            description=component_data.description
        )
        
        db.add(component)
        db.commit()
        db.refresh(component)
        
        return ApplicationComponentResponse.from_orm(component)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating application component: {str(e)}")


@router.get("/application-components", response_model=List[ApplicationComponentResponse])
async def get_application_components(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of application components."""
    components = db.query(ApplicationComponent).offset(skip).limit(limit).all()
    return [ApplicationComponentResponse.from_orm(component) for component in components]


# Interface Types endpoints
@router.post("/interface-types", response_model=InterfaceTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_interface_type(
    type_data: InterfaceTypeCreate,
    db: Session = Depends(get_db)
):
    """Create a new interface type."""
    try:
        # Check if type already exists
        existing = db.query(InterfaceType).filter(
            InterfaceType.name == type_data.name
        ).first()
        
        if existing:
            raise HTTPException(status_code=409, detail="Interface type already exists")
        
        # Create new type
        interface_type = InterfaceType(
            name=type_data.name,
            description=type_data.description
        )
        
        db.add(interface_type)
        db.commit()
        db.refresh(interface_type)
        
        return InterfaceTypeResponse.from_orm(interface_type)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating interface type: {str(e)}")


@router.get("/interface-types", response_model=List[InterfaceTypeResponse])
async def get_interface_types(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of interface types."""
    types = db.query(InterfaceType).offset(skip).limit(limit).all()
    return [InterfaceTypeResponse.from_orm(type) for type in types]


# Interfaces endpoints
@router.post("/interfaces", response_model=InterfaceResponse, status_code=status.HTTP_201_CREATED)
async def create_interface(
    interface_data: InterfaceCreate,
    db: Session = Depends(get_db)
):
    """Create a new interface."""
    try:
        # Validate application component exists
        app_component = db.query(ApplicationComponent).filter(
            ApplicationComponent.id == interface_data.application_component_id
        ).first()
        
        if not app_component:
            raise HTTPException(status_code=404, detail="Application component not found")
        
        # Validate interface type exists
        interface_type = db.query(InterfaceType).filter(
            InterfaceType.id == interface_data.interface_type_id
        ).first()
        
        if not interface_type:
            raise HTTPException(status_code=404, detail="Interface type not found")
        
        # Create new interface
        interface = Interface(
            name=interface_data.name,
            description=interface_data.description,
            application_component_id=interface_data.application_component_id,
            interface_type_id=interface_data.interface_type_id
        )
        
        db.add(interface)
        db.commit()
        db.refresh(interface)
        
        return InterfaceResponse.from_orm(interface)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating interface: {str(e)}")


@router.get("/interfaces", response_model=List[InterfaceResponse])
async def get_interfaces(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of interfaces."""
    interfaces = db.query(Interface).offset(skip).limit(limit).all()
    return [InterfaceResponse.from_orm(interface) for interface in interfaces]


# Topics endpoints
@router.get("/topics", response_model=List[TopicResponse])
async def get_topics(
    skip: int = 0,
    limit: int = 100,
    environment: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of topics."""
    query = db.query(Topic)
    
    if environment:
        query = query.filter(Topic.environment == environment)
    
    topics = query.offset(skip).limit(limit).all()
    return [TopicResponse.from_orm(topic) for topic in topics]


@router.get("/topics/{topic_id}", response_model=TopicDetailResponse)
async def get_topic(
    topic_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific topic by ID with full details."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get producers
    producers = db.query(TopicProducer).filter(TopicProducer.topic_id == topic_id).all()
    producer_names = [p.producer_name for p in producers]
    
    # Get consumers
    consumers = db.query(TopicConsumer).filter(TopicConsumer.topic_id == topic_id).all()
    consumer_names = [c.consumer_name for c in consumers]
    
    # Get missing producers
    missing_producers = db.query(MissingProducer).filter(MissingProducer.topic_id == topic_id).all()
    missing_producer_names = [mp.producer_name for mp in missing_producers]
    
    # Get missing consumers
    missing_consumers = db.query(MissingConsumer).filter(MissingConsumer.topic_id == topic_id).all()
    missing_consumer_names = [mc.consumer_name for mc in missing_consumers]
    
    # Create detailed response
    topic_dict = TopicResponse.from_orm(topic).dict()
    topic_dict.update({
        "producers": producer_names,
        "consumers": consumer_names,
        "missing_producers": missing_producer_names,
        "missing_consumers": missing_consumer_names
    })
    
    return TopicDetailResponse(**topic_dict)


# Reports endpoints
@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    report_request: ReportRequest,
    db: Session = Depends(get_db)
):
    """Generate a WOSA report."""
    try:
        report_service = WOSAReportService(db)
        report = await report_service.generate_report(
            report_request.report_type,
            report_request.parameters
        )
        
        return ReportResponse.from_orm(report)
        
    except BaseAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.get("/reports", response_model=List[ReportResponse])
async def get_reports(
    skip: int = 0,
    limit: int = 100,
    report_type: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of generated reports."""
    query = db.query(Report)
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    reports = query.offset(skip).limit(limit).all()
    return [ReportResponse.from_orm(report) for report in reports]


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific report by ID."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return ReportResponse.from_orm(report)


# ID Generation endpoint
@router.post("/generate-id", response_model=IDGenerationResponse)
async def generate_id(
    request: IDGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate next available ID for an entity."""
    try:
        id_service = IDGenerationService(db)
        result = await id_service.get_next_available_id(request.entity, request.id)
        
        return IDGenerationResponse(**result)
        
    except BaseAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating ID: {str(e)}")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for WOSA API."""
    return {"status": "healthy", "service": "WOSA Reports API"}
