import asyncpg
import aiomysql
import aiosqlite
import urllib.parse
from typing import Optional, Dict, Any, List
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.db_type = None
        self.is_connected = False

    async def connect_with_credentials(self, db_type: str, host: str = None, port: int = None, 
                                      database: str = None, username: str = None, 
                                      password: str = None) -> bool:
        """Connect using individual credentials"""
        try:
            self.db_type = db_type.lower()
            
            if self.db_type == "postgresql":
                self.connection = await asyncpg.connect(
                    host=host,
                    port=port or 5432,
                    database=database,
                    user=username,
                    password=password
                )
            elif self.db_type == "mysql":
                self.connection = await aiomysql.connect(
                    host=host,
                    port=port or 3306,
                    db=database,
                    user=username,
                    password=password,
                    autocommit=True
                )
            elif self.db_type == "sqlite":
                self.connection = await aiosqlite.connect(database)
            elif self.db_type == "sqlserver":
                # Using asyncpg with pg8000 or similar for SQL Server
                # For simplicity, raise not implemented
                raise NotImplementedError("SQL Server support coming soon")
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            self.is_connected = True
            logger.info(f"Connected to {db_type} database: {database}")
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            self.is_connected = False
            raise

    async def connect_with_string(self, connection_string: str) -> bool:
        """Connect using connection string URI"""
        try:
            # Parse connection string
            parsed = urllib.parse.urlparse(connection_string)
            
            self.db_type = parsed.scheme
            host = parsed.hostname
            port = parsed.port
            database = parsed.path.lstrip('/')
            username = parsed.username
            password = parsed.password
            
            return await self.connect_with_credentials(
                db_type=self.db_type,
                host=host,
                port=port,
                database=database,
                username=username,
                password=password
            )
            
        except Exception as e:
            logger.error(f"Connection string parsing failed: {str(e)}")
            raise

    async def disconnect(self):
        """Close database connection"""
        if self.connection:
            try:
                if self.db_type == "postgresql":
                    await self.connection.close()
                elif self.db_type == "mysql":
                    self.connection.close()
                    await self.connection.wait_closed()
                elif self.db_type == "sqlite":
                    await self.connection.close()
                
                self.is_connected = False
                logger.info("Disconnected from database")
            except Exception as e:
                logger.error(f"Error during disconnect: {str(e)}")

    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        if not self.is_connected or not self.connection:
            raise Exception("Not connected to database")
        
        try:
            if self.db_type == "postgresql":
                rows = await self.connection.fetch(query)
                return [dict(row) for row in rows]
                
            elif self.db_type == "mysql":
                async with self.connection.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query)
                    rows = await cursor.fetchall()
                    return rows
                    
            elif self.db_type == "sqlite":
                cursor = await self.connection.execute(query)
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
                
            else:
                raise NotImplementedError(f"Query execution not implemented for {self.db_type}")
                
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise

    @asynccontextmanager
    async def transaction(self):
        """Context manager for transactions"""
        if not self.is_connected:
            raise Exception("Not connected to database")
        
        if self.db_type == "postgresql":
            async with self.connection.transaction():
                yield
        else:
            # For non-PostgreSQL databases, no transaction support
            logger.warning(f"Transaction not supported for database type: {self.db_type}")
            yield