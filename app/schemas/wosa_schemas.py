"""
Pydantic schemas for WOSA Reports system.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class TopicStats(BaseModel):
    """Schema for topic statistics."""
    average_message_size: float = 0
    cleanup_policy: Optional[str] = None
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


class TopicData(BaseModel):
    """Schema for topic data from JSON."""
    bridged_topic: Optional[str] = None
    consumers: List[str] = []
    missing_consumers: List[str] = []
    missing_producers: List[str] = []
    name: str
    producers: List[str] = []
    stats: TopicStats


class WOSAReportData(BaseModel):
    """Schema for complete WOSA report JSON."""
    created_at: datetime
    topics: List[TopicData]
    
    @validator('topics')
    def validate_topics(cls, v):
        if not v:
            raise ValueError('Topics list cannot be empty')
        return v


class FileUploadRequest(BaseModel):
    """Schema for file upload request."""
    filename: str
    user_id: Optional[str] = None
    content: str  # Base64 encoded JSON content


class FileResponse(BaseModel):
    """Schema for file response."""
    id: int
    name: str
    original_name: str
    upload_date: datetime
    processing_date: Optional[datetime]
    user_id: Optional[str]
    file_size: Optional[int]
    status: str
    
    class Config:
        from_attributes = True


class ApplicationComponentCreate(BaseModel):
    """Schema for creating application component."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class ApplicationComponentResponse(BaseModel):
    """Schema for application component response."""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class InterfaceTypeCreate(BaseModel):
    """Schema for creating interface type."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class InterfaceTypeResponse(BaseModel):
    """Schema for interface type response."""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class InterfaceCreate(BaseModel):
    """Schema for creating interface."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    application_component_id: int
    interface_type_id: int


class InterfaceResponse(BaseModel):
    """Schema for interface response."""
    id: int
    name: str
    description: Optional[str]
    application_component_id: int
    interface_type_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class TopicResponse(BaseModel):
    """Schema for topic response."""
    id: int
    name: str
    file_id: int
    interface_id: Optional[int]
    environment: Optional[str]
    bridged_topic: Optional[str]
    average_message_size: float
    estimated_size: float
    last_message_date: Optional[datetime]
    last_stat_retrieval_date: Optional[datetime]
    maximum_message_size: float
    minimum_message_size: float
    messages_last_30d: int
    partition_number: int
    replication_factor: int
    retention: Optional[str]
    total_messages: int
    cleanup_policy: Optional[str]
    created_at: datetime
    updated_at: datetime
    first_seen: datetime
    last_seen: datetime
    is_deprecated: bool
    deprecated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TopicDetailResponse(TopicResponse):
    """Schema for detailed topic response with relationships."""
    producers: List[str] = []
    consumers: List[str] = []
    missing_producers: List[str] = []
    missing_consumers: List[str] = []


class ReportRequest(BaseModel):
    """Schema for report generation request."""
    report_type: int = Field(..., ge=1, le=10)
    parameters: Optional[Dict[str, Any]] = None
    generated_by: Optional[str] = None


class ReportResponse(BaseModel):
    """Schema for report response."""
    id: int
    report_type: int
    report_name: str
    generated_at: datetime
    generated_by: Optional[str]
    parameters: Optional[Dict[str, Any]]
    results_count: int
    file_path: Optional[str]
    
    class Config:
        from_attributes = True


class ReportItemResponse(BaseModel):
    """Schema for report item response."""
    id: int
    report_id: int
    topic_id: Optional[int]
    item_data: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ValidationError(BaseModel):
    """Schema for validation errors."""
    field: str
    message: str
    value: Any


class ProcessingResult(BaseModel):
    """Schema for file processing result."""
    file_id: int
    status: str
    topics_processed: int
    topics_created: int
    topics_updated: int
    errors: List[str] = []
    warnings: List[str] = []


class IDGenerationRequest(BaseModel):
    """Schema for ID generation request."""
    entity: str = Field(..., min_length=1)
    id: int = Field(..., ge=1)


class IDGenerationResponse(BaseModel):
    """Schema for ID generation response."""
    entity: str
    requested_id: int
    available_id: int
    is_available: bool
