from typing import List, Dict, Any
import logging
from .connection import DatabaseConnection

logger = logging.getLogger(__name__)

class DatabaseSchema:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection

    async def get_schema(self) -> List[Dict[str, Any]]:
        """Get database schema (tables, columns, types, constraints)"""
        if not self.db.is_connected:
            raise Exception("Not connected to database")
        
        try:
            if self.db.db_type == "postgresql":
                return await self._get_postgresql_schema()
            elif self.db.db_type == "mysql":
                return await self._get_mysql_schema()
            elif self.db.db_type == "sqlite":
                return await self._get_sqlite_schema()
            else:
                raise NotImplementedError(f"Schema fetching not implemented for {self.db.db_type}")
                
        except Exception as e:
            logger.error(f"Schema fetch failed: {str(e)}")
            raise

    async def _get_postgresql_schema(self) -> List[Dict[str, Any]]:
        """Get PostgreSQL schema"""
        query = """
        SELECT 
            t.table_name,
            json_agg(
                json_build_object(
                    'name', c.column_name,
                    'type', c.data_type,
                    'nullable', c.is_nullable = 'YES',
                    'isPrimary', CASE WHEN pk.constraint_type = 'PRIMARY KEY' THEN true ELSE false END
                )
            ) as columns,
            (SELECT reltuples::bigint FROM pg_class WHERE relname = t.table_name) as row_count
        FROM information_schema.tables t
        JOIN information_schema.columns c ON t.table_name = c.table_name AND t.table_schema = c.table_schema
        LEFT JOIN (
            SELECT kcu.table_name, kcu.column_name, tc.constraint_type
            FROM information_schema.key_column_usage kcu
            JOIN information_schema.table_constraints tc 
                ON kcu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
        ) pk ON c.table_name = pk.table_name AND c.column_name = pk.column_name
        WHERE t.table_schema = 'public' 
            AND t.table_type = 'BASE TABLE'
        GROUP BY t.table_name
        ORDER BY t.table_name;
        """
        results = await self.db.execute_query(query)
        return results

    async def _get_mysql_schema(self) -> List[Dict[str, Any]]:
        """Get MySQL schema"""
        query = """
        SELECT 
            t.TABLE_NAME as table_name,
            JSON_ARRAYAGG(
                JSON_OBJECT(
                    'name', c.COLUMN_NAME,
                    'type', c.DATA_TYPE,
                    'nullable', c.IS_NULLABLE = 'YES',
                    'isPrimary', c.COLUMN_KEY = 'PRI'
                )
            ) as columns,
            t.TABLE_ROWS as row_count
        FROM information_schema.TABLES t
        JOIN information_schema.COLUMNS c 
            ON t.TABLE_NAME = c.TABLE_NAME 
            AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
        WHERE t.TABLE_SCHEMA = DATABASE()
        GROUP BY t.TABLE_NAME, t.TABLE_ROWS;
        """
        results = await self.db.execute_query(query)
        return results

    async def _get_sqlite_schema(self) -> List[Dict[str, Any]]:
        """Get SQLite schema"""
        # Get all tables
        tables_query = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%';
        """
        tables = await self.db.execute_query(tables_query)
        
        schema = []
        for table in tables:
            table_name = table['name']
            
            # Get columns for each table
            pragma_query = f"PRAGMA table_info({table_name});"
            columns_info = await self.db.execute_query(pragma_query)
            
            columns = []
            for col in columns_info:
                columns.append({
                    'name': col['name'],
                    'type': col['type'],
                    'nullable': not col['notnull'],
                    'isPrimary': col['pk'] == 1
                })
            
            # Get row count
            count_query = f"SELECT COUNT(*) as count FROM {table_name};"
            count_result = await self.db.execute_query(count_query)
            row_count = count_result[0]['count'] if count_result else 0
            
            schema.append({
                'table_name': table_name,
                'columns': columns,
                'row_count': row_count
            })
        
        return schema