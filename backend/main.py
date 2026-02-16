from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import time
from contextlib import asynccontextmanager
import asyncpg
import aiomysql
import aiosqlite
import pyodbc  # for SQL Server
import urllib.parse
import json

from models.sql_models import (
    DatabaseType, 
    ConnectionCredentials, 
    ConnectionResponse,
    DisconnectResponse,
    TextToSQLRequest, 
    TextToSQLResponse, 
    ExplainRequest,
    ExplainResponse, 
    ValidateSQLRequest,  
    ValidateSQLResponse, 
    SchemaResponse, 
    QueryHistory
)

from services.sql_generator import SQLGenerator
from services.sql_explainer import SQLExplainer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
class AppState:
    def __init__(self):
        self.db_connection = None
        self.db_type = None
        self.db_name = None
        self.is_connected = False
        self.sql_generator = None
        self.sql_explainer = None
        self.query_history = []

state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Text-to-SQL Backend...")
    state.sql_generator = SQLGenerator()
    state.sql_explainer = SQLExplainer()
    yield
    # Shutdown
    if state.is_connected and state.db_connection:
        await disconnect_database()
    logger.info("Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Text-to-SQL Backend",
    description="Convert natural language to SQL using Ollama SQLCoder",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Request/Response Models (matching UI)
class ConnectRequest(BaseModel):
    db_type: str
    host: Optional[str] = "localhost"
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_string: Optional[str] = None
    use_uri: bool = False

class ConnectResponse(BaseModel):
    message: str
    status: str
    database_type: Optional[str] = None
    database_name: Optional[str] = None

class SchemaResponse(BaseModel):
    tables: List[Dict[str, Any]]

# Database Connection Routes
@app.post("/api/connect", response_model=ConnectResponse)
async def connect_database(credentials: ConnectRequest):
    """Connect to database using credentials or connection URI"""
    try:
        logger.info(f"Connecting to {credentials.db_type} database...")
        
        # Handle connection string if provided
        if credentials.use_uri and credentials.connection_string:
            success = await connect_with_uri(credentials.connection_string)
        else:
            success = await connect_with_credentials(credentials)
        
        if success:
            # Fetch and store schema for later use
            await fetch_schema()
            
            return ConnectResponse(
                message="Connected successfully!",
                status="connected",
                database_type=state.db_type,
                database_name=state.db_name
            )
        else:
            raise HTTPException(status_code=400, detail="Connection failed")
            
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/disconnect")
async def disconnect_database():
    """Disconnect from database"""
    global state
    if state.is_connected and state.db_connection:
        try:
            if state.db_type == DatabaseType.POSTGRESQL:
                await state.db_connection.close()
            elif state.db_type == DatabaseType.MYSQL:
                state.db_connection.close()
                await state.db_connection.wait_closed()
            elif state.db_type == DatabaseType.SQLITE:
                await state.db_connection.close()
            elif state.db_type == DatabaseType.SQLSERVER:
                state.db_connection.close()
            
            state.is_connected = False
            state.db_connection = None
            state.db_type = None
            state.db_name = None
            logger.info("Disconnected from database")
            
            return DisconnectResponse(message="Disconnected successfully")
        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    return DisconnectResponse(message="Already disconnected")


@app.get("/api/schema", response_model=SchemaResponse)
async def get_schema():
    """Get database schema for Schema tab in UI"""
    if not state.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to database")
    
    try:
        tables = await fetch_schema()
        return SchemaResponse(tables=tables)
    except Exception as e:
        logger.error(f"Schema fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/api/text-to-sql", response_model=TextToSQLResponse)
async def text_to_sql(request: TextToSQLRequest):
    """Convert natural language to SQL"""
    start_time = time.time()
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Get schema if connected
        schema_data = None
        if state.is_connected:
            logger.info("🔄 Database is connected, fetching schema...")
            schema_data = await fetch_schema()
            
            # 🔴 CRITICAL DEBUGGING
            logger.info("=" * 60)
            logger.info(f"SCHEMA FETCH RESULT:")
            logger.info(f"Schema type: {type(schema_data)}")
            logger.info(f"Schema length: {len(schema_data)}")
            
            if schema_data and len(schema_data) > 0:
                logger.info(f"First table: {schema_data[0]}")
                # Extract table names
                table_names = []
                for table in schema_data:
                    if isinstance(table, dict):
                        name = table.get('name') or table.get('table_name', 'unknown')
                        table_names.append(name)
                logger.info(f"Tables in schema: {table_names}")
            else:
                logger.warning("⚠️ Schema data is empty or None!")
            logger.info("=" * 60)
        else:
            logger.warning("⚠️ Not connected to database!")
        
        # Generate SQL using Ollama SQLCoder
        logger.info(f"Calling SQLGenerator.generate with schema of length: {len(schema_data) if schema_data else 0}")
        sql = await state.sql_generator.generate(
            natural_language_query=request.query,
            schema=schema_data
        )
        
        # CRITICAL: Verify SQL is not empty
        if not sql or sql.strip() == "":
            logger.error("❌ Generated SQL is empty!")
            sql = f"-- Error: Could not generate SQL for: {request.query}"
        
        logger.info(f"✅ Final SQL to return: {sql[:100]}...")
        
        results = None
        execution_time = None
        error = None
        
        # Execute if connected and requested
        if state.is_connected and request.execute:
            execution_start = time.time()
            try:
                results = await execute_query(sql, request.limit)
                execution_time = time.time() - execution_start
                logger.info(f"Query executed, returned {len(results) if results else 0} rows")
            except Exception as e:
                error = str(e)
                logger.warning(f"Query execution failed: {error}")
        
        # Add to history
        history_item = {
            "id": len(state.query_history) + 1,
            "query": request.query,
            "sql": sql,
            "timestamp": time.time(),
            "status": "success" if results is not None else "error" if error else "pending"
        }
        state.query_history.append(history_item)
        
        # Create response dictionary explicitly
        response_dict = {
            "sql": sql,
            "results": results,
            "error": error,
            "execution_time": execution_time,
            "row_count": len(results) if results else 0
        }
        
        logger.info(f"📤 Response dict: {response_dict}")
        
        # Return as Pydantic model
        return TextToSQLResponse(**response_dict)
        
    except Exception as e:
        logger.error(f"Text-to-SQL error: {str(e)}")
        error_response = {
            "sql": f"-- Error: {str(e)}",
            "results": None,
            "error": str(e),
            "execution_time": None,
            "row_count": 0
        }
        return TextToSQLResponse(**error_response)

@app.post("/api/explain", response_model=ExplainResponse)
async def explain_sql(request: ExplainRequest):
    """Explain SQL query in plain English"""
    try:
        explanation = await state.sql_explainer.explain(request.sql)
        return ExplainResponse(explanation=explanation)
    except Exception as e:
        logger.error(f"Explain error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history(limit: int = 50):
    """Get query history for History tab in UI"""
    return {
        "queries": state.query_history[-limit:]
    }

@app.post("/api/validate")
async def validate_sql(request: ValidateSQLRequest):
    """Validate SQL query without executing"""
    try:
        # Basic SQL validation
        is_valid, message = await validate_query(request.sql)
        return ValidateSQLResponse(
            valid=is_valid,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database_connected": state.is_connected,
        "database_type": state.db_type,
        "database_name": state.db_name,
        "ollama_available": await state.sql_generator.check_availability() if state.sql_generator else False
    }

# Helper Functions
async def connect_with_credentials(credentials: ConnectRequest):
    """Connect using individual credentials"""
    try:
        state.db_type = credentials.db_type.lower()
        
        if state.db_type == DatabaseType.POSTGRESQL:
            state.db_connection = await asyncpg.connect(
                host=credentials.host,
                port=credentials.port or 5433,
                database=credentials.database,
                user=credentials.username,
                password=credentials.password
            )
            state.db_name = credentials.database
            
        elif state.db_type == DatabaseType.MYSQL:
            state.db_connection = await aiomysql.connect(
                host=credentials.host,
                port=credentials.port or 3306,
                db=credentials.database,
                user=credentials.username,
                password=credentials.password,
                autocommit=True
            )
            state.db_name = credentials.database
            
        elif state.db_type == DatabaseType.SQLITE:
            state.db_connection = await aiosqlite.connect(credentials.database)
            state.db_name = credentials.database
            
        elif state.db_type == DatabaseType.SQLSERVER:
            # SQL Server connection using pyodbc
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={credentials.host},{credentials.port or 1433};"
                f"DATABASE={credentials.database};"
                f"UID={credentials.username};"
                f"PWD={credentials.password}"
            )
            state.db_connection = pyodbc.connect(conn_str)
            state.db_name = credentials.database
        
        state.is_connected = True
        logger.info(f"Connected to {state.db_type} database: {state.db_name}")
        return True
        
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
        state.is_connected = False
        raise e

async def connect_with_uri(uri: str):
    """Connect using connection URI"""
    try:
        parsed = urllib.parse.urlparse(uri)
        
        credentials = ConnectRequest(
            db_type=parsed.scheme,
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path.lstrip('/'),
            username=parsed.username,
            password=parsed.password,
            use_uri=True
        )
        
        return await connect_with_credentials(credentials)
        
    except Exception as e:
        logger.error(f"URI connection failed: {str(e)}")
        raise e

async def fetch_schema() -> List[Dict[str, Any]]:
    """Fetch database schema for Schema tab - works with any database"""
    if not state.is_connected:
        logger.warning("Cannot fetch schema: Not connected to database")
        return []
    
    try:
        logger.info(f"Fetching schema for {state.db_type} database")
        
        if state.db_type == DatabaseType.POSTGRESQL:
            return await fetch_postgresql_schema()
        elif state.db_type == DatabaseType.MYSQL:
            return await fetch_mysql_schema()
        elif state.db_type == DatabaseType.SQLITE:
            return await fetch_sqlite_schema()
        elif state.db_type == DatabaseType.SQLSERVER:
            return await fetch_sqlserver_schema()
        else:
            logger.warning(f"Unsupported database type: {state.db_type}")
            return []
            
    except Exception as e:
        logger.error(f"Schema fetch failed: {str(e)}")
        return []

async def fetch_postgresql_schema() -> List[Dict[str, Any]]:
    """Fetch PostgreSQL schema"""
    try:
        # Get all tables
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        table_rows = await state.db_connection.fetch(tables_query)
        
        schema = []
        for table_row in table_rows:
            table_name = table_row['table_name']
            
            # Get columns for this table
            columns_query = """
            SELECT 
                column_name,
                data_type,
                is_nullable = 'YES' as nullable,
                EXISTS (
                    SELECT 1 
                    FROM information_schema.key_column_usage k
                    JOIN information_schema.table_constraints tc 
                        ON k.constraint_name = tc.constraint_name
                    WHERE k.table_name = c.table_name 
                    AND k.column_name = c.column_name
                    AND tc.constraint_type = 'PRIMARY KEY'
                ) as is_primary
            FROM information_schema.columns c
            WHERE table_name = $1 AND table_schema = 'public'
            ORDER BY ordinal_position;
            """
            column_rows = await state.db_connection.fetch(columns_query, table_name)
            
            columns = []
            for col in column_rows:
                columns.append({
                    "name": col['column_name'],
                    "type": col['data_type'],
                    "nullable": col['nullable'],
                    "isPrimary": col['is_primary']
                })
            
            # Get row count (estimate for performance)
            try:
                count_query = f'SELECT COUNT(*) as count FROM "{table_name}"'
                count_result = await state.db_connection.fetch(count_query)
                row_count = count_result[0]['count'] if count_result else 0
            except:
                row_count = 0
            
            schema.append({
                "name": table_name,
                "columns": columns,
                "rowCount": row_count
            })
        
        logger.info(f"PostgreSQL: Fetched {len(schema)} tables: {[t['name'] for t in schema]}")
        return schema
        
    except Exception as e:
        logger.error(f"Error fetching PostgreSQL schema: {str(e)}")
        return []

async def fetch_mysql_schema() -> List[Dict[str, Any]]:
    """Fetch MySQL schema"""
    try:
        # Get all tables and columns
        query = """
        SELECT 
            TABLE_NAME,
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_KEY = 'PRI' as IS_PRIMARY
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME, ORDINAL_POSITION;
        """
        
        async with state.db_connection.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            rows = await cursor.fetchall()
            
            # Group by table
            tables_dict = {}
            for row in rows:
                table_name = row['TABLE_NAME']
                if table_name not in tables_dict:
                    tables_dict[table_name] = {
                        "name": table_name,
                        "columns": [],
                        "rowCount": 0
                    }
                
                tables_dict[table_name]["columns"].append({
                    "name": row['COLUMN_NAME'],
                    "type": row['DATA_TYPE'],
                    "nullable": row['IS_NULLABLE'] == 'YES',
                    "isPrimary": row['IS_PRIMARY']
                })
            
            # Get row counts for each table
            for table_name in tables_dict:
                try:
                    async with state.db_connection.cursor() as count_cursor:
                        await count_cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                        count_result = await count_cursor.fetchone()
                        tables_dict[table_name]["rowCount"] = count_result[0] if count_result else 0
                except:
                    tables_dict[table_name]["rowCount"] = 0
            
            schema = list(tables_dict.values())
            logger.info(f"MySQL: Fetched {len(schema)} tables: {[t['name'] for t in schema]}")
            return schema
            
    except Exception as e:
        logger.error(f"Error fetching MySQL schema: {str(e)}")
        return []

async def fetch_sqlite_schema() -> List[Dict[str, Any]]:
    """Fetch SQLite schema"""
    try:
        tables = []
        
        # Get all tables
        cursor = await state.db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
        )
        table_rows = await cursor.fetchall()
        
        for table_row in table_rows:
            table_name = table_row[0]
            
            # Get columns
            cursor = await state.db_connection.execute(f"PRAGMA table_info(`{table_name}`)")
            columns_data = await cursor.fetchall()
            
            columns = []
            for col in columns_data:
                columns.append({
                    "name": col[1],
                    "type": col[2],
                    "nullable": not col[3],
                    "isPrimary": col[5] == 1
                })
            
            # Get row count
            try:
                cursor = await state.db_connection.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                count = await cursor.fetchone()
                row_count = count[0] if count else 0
            except:
                row_count = 0
            
            tables.append({
                "name": table_name,
                "columns": columns,
                "rowCount": row_count
            })
        
        logger.info(f"SQLite: Fetched {len(tables)} tables: {[t['name'] for t in tables]}")
        return tables
        
    except Exception as e:
        logger.error(f"Error fetching SQLite schema: {str(e)}")
        return []

async def fetch_sqlserver_schema() -> List[Dict[str, Any]]:
    """Fetch SQL Server schema"""
    try:
        cursor = state.db_connection.cursor()
        
        # Get all tables and columns
        query = """
        SELECT 
            t.TABLE_NAME,
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.IS_NULLABLE,
            CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END as IS_PRIMARY
        FROM INFORMATION_SCHEMA.TABLES t
        JOIN INFORMATION_SCHEMA.COLUMNS c 
            ON t.TABLE_NAME = c.TABLE_NAME
        LEFT JOIN (
            SELECT ku.TABLE_NAME, ku.COLUMN_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku
                ON tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
            WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
        ) pk ON c.TABLE_NAME = pk.TABLE_NAME AND c.COLUMN_NAME = pk.COLUMN_NAME
        WHERE t.TABLE_TYPE = 'BASE TABLE'
        ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION;
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Group by table
        tables_dict = {}
        for row in rows:
            table_name = row[0]
            if table_name not in tables_dict:
                tables_dict[table_name] = {
                    "name": table_name,
                    "columns": [],
                    "rowCount": 0
                }
            
            tables_dict[table_name]["columns"].append({
                "name": row[1],
                "type": row[2],
                "nullable": row[3] == 'YES',
                "isPrimary": row[4]
            })
        
        # Get row counts for each table
        for table_name in tables_dict:
            try:
                count_cursor = state.db_connection.cursor()
                count_cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
                count_result = count_cursor.fetchone()
                tables_dict[table_name]["rowCount"] = count_result[0] if count_result else 0
            except:
                tables_dict[table_name]["rowCount"] = 0
        
        schema = list(tables_dict.values())
        logger.info(f"SQL Server: Fetched {len(schema)} tables: {[t['name'] for t in schema]}")
        return schema
        
    except Exception as e:
        logger.error(f"Error fetching SQL Server schema: {str(e)}")
        return []

async def fetch_sqlite_schema():
    """Fetch SQLite schema"""
    try:
        tables = []
        
        # Get all tables
        cursor = await state.db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
        )
        table_rows = await cursor.fetchall()
        
        for table_row in table_rows:
            table_name = table_row[0]
            
            # Get columns
            cursor = await state.db_connection.execute(f"PRAGMA table_info(`{table_name}`)")
            columns_data = await cursor.fetchall()
            
            columns = []
            for col in columns_data:
                columns.append({
                    "name": col[1],
                    "type": col[2],
                    "nullable": not col[3],
                    "isPrimary": col[5] == 1
                })
            
            # Get row count
            try:
                cursor = await state.db_connection.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                count = await cursor.fetchone()
                row_count = count[0] if count else 0
            except:
                row_count = 0
            
            tables.append({
                "name": table_name,
                "columns": columns,
                "rowCount": row_count
            })
        
        logger.info(f"SQLite: Fetched {len(tables)} tables: {[t['name'] for t in tables]}")
        return tables
        
    except Exception as e:
        logger.error(f"Error fetching SQLite schema: {str(e)}")
        return []

async def fetch_sqlserver_schema():
    """Fetch SQL Server schema"""
    try:
        cursor = state.db_connection.cursor()
        
        # Get all tables and columns
        query = """
        SELECT 
            t.TABLE_NAME,
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.IS_NULLABLE,
            CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END as IS_PRIMARY
        FROM INFORMATION_SCHEMA.TABLES t
        JOIN INFORMATION_SCHEMA.COLUMNS c 
            ON t.TABLE_NAME = c.TABLE_NAME
        LEFT JOIN (
            SELECT ku.TABLE_NAME, ku.COLUMN_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku
                ON tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
            WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
        ) pk ON c.TABLE_NAME = pk.TABLE_NAME AND c.COLUMN_NAME = pk.COLUMN_NAME
        WHERE t.TABLE_TYPE = 'BASE TABLE'
        ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION;
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Group by table
        tables_dict = {}
        for row in rows:
            table_name = row[0]
            if table_name not in tables_dict:
                tables_dict[table_name] = {
                    "name": table_name,
                    "columns": [],
                    "rowCount": 0
                }
            
            tables_dict[table_name]["columns"].append({
                "name": row[1],
                "type": row[2],
                "nullable": row[3] == 'YES',
                "isPrimary": row[4]
            })
        
        # Get row counts for each table
        for table_name in tables_dict:
            try:
                count_cursor = state.db_connection.cursor()
                count_cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
                count_result = count_cursor.fetchone()
                tables_dict[table_name]["rowCount"] = count_result[0] if count_result else 0
            except:
                tables_dict[table_name]["rowCount"] = 0
        
        schema = list(tables_dict.values())
        logger.info(f"SQL Server: Fetched {len(schema)} tables: {[t['name'] for t in schema]}")
        return schema
        
    except Exception as e:
        logger.error(f"Error fetching SQL Server schema: {str(e)}")
        return []

async def execute_query(sql: str, limit: Optional[int] = None):
    """Execute SQL query and return results"""
    if not state.is_connected:
        raise Exception("Not connected to database")
    
    # Add LIMIT if not present and limit is specified
    if limit and "LIMIT" not in sql.upper():
        sql += f" LIMIT {limit}"
    
    try:
        if state.db_type == DatabaseType.POSTGRESQL:
            rows = await state.db_connection.fetch(sql)
            return [dict(row) for row in rows]
            
        elif state.db_type == DatabaseType.MYSQL:
            async with state.db_connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(sql)
                rows = await cursor.fetchall()
                return rows
                
        elif state.db_type == DatabaseType.SQLITE:
            cursor = await state.db_connection.execute(sql)
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
            
        elif state.db_type == DatabaseType.SQLSERVER:
            cursor = state.db_connection.cursor()
            cursor.execute(sql)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
            
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        raise e

async def validate_query(sql: str):
    """Basic SQL validation"""
    sql_upper = sql.upper().strip()
    
    # Check for dangerous operations
    dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
    
    first_word = sql_upper.split()[0] if sql_upper.split() else ''
    
    if first_word not in ['SELECT', 'WITH', 'EXPLAIN', 'SHOW', 'DESCRIBE']:
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False, f"Dangerous operation detected: {keyword}"
    
    return True, "Query is valid"

@app.get("/api/debug-schema")
async def debug_schema():
    """Debug endpoint to check schema fetching"""
    if not state.is_connected:
        return {
            "connected": False,
            "message": "Not connected to database"
        }
    
    try:
        schema = await fetch_schema()
        return {
            "connected": True,
            "database": state.db_name,
            "db_type": state.db_type,
            "schema_length": len(schema),
            "tables": [t.get('name', 'unknown') for t in schema if isinstance(t, dict)][:10],
            "sample_table": schema[0] if schema else None
        }
    except Exception as e:
        return {
            "connected": True,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )