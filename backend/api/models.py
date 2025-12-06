"""
API Models - Pydantic models for request/response validation
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class NLQueryRequest(BaseModel):
    """Request model for natural language to SQL conversion"""
    question: str = Field(..., description="Natural language question", min_length=1)
    max_retries: int = Field(
        default=3,
        description="Maximum number of SQL debug retry attempts",
        ge=0,
        le=5
    )
    confidence_threshold: float = Field(
        default=0.7,
        description="Minimum confidence threshold (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )


class SQLResponse(BaseModel):
    """Response model for SQL generation"""
    success: bool = Field(..., description="Whether the request succeeded")
    question: str = Field(..., description="Original question")
    sql: Optional[str] = Field(None, description="Generated SQL query")
    results: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Query results"
    )
    row_count: int = Field(default=0, description="Number of rows returned")
    column_names: List[str] = Field(
        default_factory=list,
        description="Column names in results"
    )
    confidence: float = Field(default=0.0, description="Confidence score (0.0 to 1.0)")
    evaluation: Optional[Dict[str, Any]] = Field(
        None,
        description="Quality evaluation details"
    )
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Pipeline execution metadata"
    )


class TableSchema(BaseModel):
    """Schema information for a table"""
    name: str
    columns: List[Dict[str, Any]]
    primary_keys: List[str] = Field(default_factory=list)
    foreign_keys: List[Dict[str, str]] = Field(default_factory=list)
    description: str = ""


class SchemaResponse(BaseModel):
    """Response model for schema information"""
    success: bool
    tables: Dict[str, TableSchema] = Field(default_factory=dict)
    relationships: List[Dict[str, str]] = Field(default_factory=list)
    num_tables: int = 0
    total_columns: int = 0


class InitializeRequest(BaseModel):
    """Request model for initialization"""
    force_refresh: bool = Field(
        default=False,
        description="Force re-generation of embeddings"
    )


class InitializeResponse(BaseModel):
    """Response model for initialization"""
    success: bool
    message: str
    num_tables: int = 0
    total_columns: int = 0
    num_embeddings: int = 0


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    database_connected: bool
    embeddings_loaded: bool
    version: str = "1.0.0"
