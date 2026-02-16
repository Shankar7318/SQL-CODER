from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum
import re

class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    SQLSERVER = "sqlserver"

class ConnectionCredentials(BaseModel):
    db_type: DatabaseType
    host: Optional[str] = "localhost"
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_string: Optional[str] = None
    use_uri: bool = False
    
    @validator('port', always=True)
    def set_default_port(cls, v, values):
        if v is not None:
            return v
        db_type = values.get('db_type')
        if db_type == DatabaseType.POSTGRESQL:
            return 5432
        elif db_type == DatabaseType.MYSQL:
            return 3306
        elif db_type == DatabaseType.SQLSERVER:
            return 1433
        return v

class ConnectionResponse(BaseModel):
    message: str
    status: str
    database_type: Optional[str] = None
    database_name: Optional[str] = None

class DisconnectResponse(BaseModel):
    message: str

class TextToSQLRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    execute: bool = False
    limit: Optional[int] = Field(100, ge=1, le=10000)

class TextToSQLResponse(BaseModel):
    sql: str
    results: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    row_count: Optional[int] = None

class ExplainRequest(BaseModel):
    sql: str

class ExplainResponse(BaseModel):
    explanation: str

class ValidateSQLRequest(BaseModel):
    sql: str

class ValidateSQLResponse(BaseModel):
    valid: bool
    message: str

class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool
    isPrimary: bool

class TableInfo(BaseModel):
    name: str
    columns: List[ColumnInfo]
    rowCount: Optional[int] = None

class QueryHistory(BaseModel):
    id: int
    query: str
    sql: str
    timestamp: float
    status: str

class SchemaResponse(BaseModel):
    tables: List[Dict[str, Any]]