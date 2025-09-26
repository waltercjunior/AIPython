"""
Database models for WOSA Reports system.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database import Base


class File(Base):
    """Model for uploaded JSON files."""
    
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    original_name = Column(String(255), nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processing_date = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, error
    
    # Relationships
    topics = relationship("Topic", back_populates="file")


class ApplicationComponent(Base):
    """Model for Application Components (VladSystem)."""
    
    __tablename__ = "application_components"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    interfaces = relationship("Interface", back_populates="application_component")


class InterfaceType(Base):
    """Model for Interface Types."""
    
    __tablename__ = "interface_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    interfaces = relationship("Interface", back_populates="interface_type")


class Interface(Base):
    """Model for Interfaces."""
    
    __tablename__ = "interfaces"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    application_component_id = Column(Integer, ForeignKey("application_components.id"), nullable=False)
    interface_type_id = Column(Integer, ForeignKey("interface_types.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    application_component = relationship("ApplicationComponent", back_populates="interfaces")
    interface_type = relationship("InterfaceType", back_populates="interfaces")
    topics = relationship("Topic", back_populates="interface")


class Topic(Base):
    """Model for Kafka Topics."""
    
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    interface_id = Column(Integer, ForeignKey("interfaces.id"), nullable=True)
    environment = Column(String(50), nullable=True)  # dev, prod, e2e
    bridged_topic = Column(String(255), nullable=True)
    
    # Topic statistics
    average_message_size = Column(Float, default=0)
    estimated_size = Column(Float, default=0)
    last_message_date = Column(DateTime(timezone=True), nullable=True)
    last_stat_retrieval_date = Column(DateTime(timezone=True), nullable=True)
    maximum_message_size = Column(Float, default=0)
    minimum_message_size = Column(Float, default=0)
    messages_last_30d = Column(Integer, default=0)
    partition_number = Column(Integer, default=1)
    replication_factor = Column(Integer, default=1)
    retention = Column(String(50), nullable=True)
    total_messages = Column(Integer, default=0)
    cleanup_policy = Column(String(50), nullable=True)
    
    # Status tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    is_deprecated = Column(Boolean, default=False)
    deprecated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    file = relationship("File", back_populates="topics")
    interface = relationship("Interface", back_populates="topics")
    producers = relationship("TopicProducer", back_populates="topic")
    consumers = relationship("TopicConsumer", back_populates="topic")
    missing_producers = relationship("MissingProducer", back_populates="topic")
    missing_consumers = relationship("MissingConsumer", back_populates="topic")


class TopicProducer(Base):
    """Model for Topic Producers."""
    
    __tablename__ = "topic_producers"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    producer_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    topic = relationship("Topic", back_populates="producers")


class TopicConsumer(Base):
    """Model for Topic Consumers."""
    
    __tablename__ = "topic_consumers"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    consumer_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    topic = relationship("Topic", back_populates="consumers")


class MissingProducer(Base):
    """Model for Missing Producers."""
    
    __tablename__ = "missing_producers"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    producer_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    topic = relationship("Topic", back_populates="missing_producers")


class MissingConsumer(Base):
    """Model for Missing Consumers."""
    
    __tablename__ = "missing_consumers"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    consumer_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    topic = relationship("Topic", back_populates="missing_consumers")


class TopicHistory(Base):
    """Model for Topic History tracking."""
    
    __tablename__ = "topic_history"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    action = Column(String(50), nullable=False)  # created, updated, deprecated
    changes = Column(JSON, nullable=True)  # Store changes as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    topic = relationship("Topic")
    file = relationship("File")


class Report(Base):
    """Model for Generated Reports."""
    
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(Integer, nullable=False)  # 1-10 as per requirements
    report_name = Column(String(255), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    generated_by = Column(String(100), nullable=True)
    parameters = Column(JSON, nullable=True)  # Store report parameters
    results_count = Column(Integer, default=0)
    file_path = Column(String(500), nullable=True)  # Path to generated report file
    
    # Relationships
    report_items = relationship("ReportItem", back_populates="report")


class ReportItem(Base):
    """Model for Report Items."""
    
    __tablename__ = "report_items"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    item_data = Column(JSON, nullable=True)  # Store item-specific data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    report = relationship("Report", back_populates="report_items")
    topic = relationship("Topic")
