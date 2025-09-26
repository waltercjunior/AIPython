"""
Domain entities for WOSA Reports system.
"""
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class WOSAFile:
    """WOSA file domain entity."""
    
    id: Optional[int] = None
    name: str = ""
    original_name: str = ""
    upload_date: Optional[datetime] = None
    processing_date: Optional[datetime] = None
    user_id: Optional[str] = None
    file_size: Optional[int] = None
    status: str = "pending"
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.upload_date is None:
            self.upload_date = datetime.utcnow()
    
    def mark_as_processing(self):
        """Mark file as processing."""
        self.status = "processing"
        self.processing_date = datetime.utcnow()
    
    def mark_as_completed(self):
        """Mark file as completed."""
        self.status = "completed"
    
    def mark_as_error(self):
        """Mark file as error."""
        self.status = "error"


@dataclass
class WOSATopic:
    """WOSA topic domain entity."""
    
    id: Optional[int] = None
    name: str = ""
    file_id: Optional[int] = None
    interface_id: Optional[int] = None
    environment: Optional[str] = None
    bridged_topic: Optional[str] = None
    
    # Statistics
    average_message_size: float = 0
    estimated_size: float = 0
    last_message_date: Optional[datetime] = None
    last_stat_retrieval_date: Optional[datetime] = None
    maximum_message_size: float = 0
    minimum_message_size: float = 0
    messages_last_30d: int = 0
    partition_number: int = 1
    replication_factor: int = 1
    retention: Optional[str] = None
    total_messages: int = 0
    cleanup_policy: Optional[str] = None
    
    # Status tracking
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    is_deprecated: bool = False
    deprecated_at: Optional[datetime] = None
    
    # Relationships
    producers: List[str] = None
    consumers: List[str] = None
    missing_producers: List[str] = None
    missing_consumers: List[str] = None
    
    def __post_init__(self):
        """Initialize lists and timestamps."""
        if self.producers is None:
            self.producers = []
        if self.consumers is None:
            self.consumers = []
        if self.missing_producers is None:
            self.missing_producers = []
        if self.missing_consumers is None:
            self.missing_consumers = []
        
        now = datetime.utcnow()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
        if self.first_seen is None:
            self.first_seen = now
        if self.last_seen is None:
            self.last_seen = now
    
    def update_stats(self, stats_data: dict):
        """Update topic statistics."""
        for key, value in stats_data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        self.last_seen = datetime.utcnow()
    
    def detect_environment(self) -> Optional[str]:
        """Detect environment from topic name."""
        name_lower = self.name.lower()
        
        if any(env in name_lower for env in ['dev', 'development']):
            return 'dev'
        elif any(env in name_lower for env in ['prod', 'production']):
            return 'prod'
        elif any(env in name_lower for env in ['e2e', 'test']):
            return 'e2e'
        
        return None
    
    def is_stale(self, days: int = 30) -> bool:
        """Check if topic is stale (no messages for specified days)."""
        if not self.last_message_date:
            return True
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.last_message_date < cutoff_date
    
    def has_producers(self) -> bool:
        """Check if topic has producers."""
        return len(self.producers) > 0
    
    def has_consumers(self) -> bool:
        """Check if topic has consumers."""
        return len(self.consumers) > 0
    
    def has_multiple_producers(self) -> bool:
        """Check if topic has multiple producers."""
        return len(self.producers) > 1
    
    def mark_as_deprecated(self):
        """Mark topic as deprecated."""
        self.is_deprecated = True
        self.deprecated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


@dataclass
class ApplicationComponent:
    """Application component domain entity."""
    
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        now = datetime.utcnow()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
    
    def activate(self):
        """Activate the component."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate the component."""
        self.is_active = False
        self.updated_at = datetime.utcnow()


@dataclass
class Interface:
    """Interface domain entity."""
    
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    application_component_id: Optional[int] = None
    interface_type_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        now = datetime.utcnow()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
    
    def activate(self):
        """Activate the interface."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate the interface."""
        self.is_active = False
        self.updated_at = datetime.utcnow()


@dataclass
class WOSAReport:
    """WOSA report domain entity."""
    
    id: Optional[int] = None
    report_type: int = 1
    report_name: str = ""
    generated_at: Optional[datetime] = None
    generated_by: Optional[str] = None
    parameters: Optional[dict] = None
    results_count: int = 0
    file_path: Optional[str] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.generated_at is None:
            self.generated_at = datetime.utcnow()
        if self.parameters is None:
            self.parameters = {}
    
    def set_results_count(self, count: int):
        """Set the number of results."""
        self.results_count = count
    
    def add_parameter(self, key: str, value: any):
        """Add a parameter to the report."""
        if self.parameters is None:
            self.parameters = {}
        self.parameters[key] = value
