
import re
from typing import Dict, Any, Optional

def parse_connection_string(connection_string: str) -> Dict[str, Any]:
    """Parse database connection string into components"""
    # Basic regex for connection string parsing
    pattern = r'^(?P<scheme>\w+)://(?:(?P<username>[^:@]+)(?::(?P<password>[^@]+))?@)?(?P<host>[^:/]+)(?::(?P<port>\d+))?/(?P<database>.+)$'
    
    match = re.match(pattern, connection_string)
    if not match:
        raise ValueError("Invalid connection string format")
    
    return {
        'db_type': match.group('scheme'),
        'username': match.group('username'),
        'password': match.group('password'),
        'host': match.group('host'),
        'port': int(match.group('port')) if match.group('port') else None,
        'database': match.group('database')
    }

def validate_sql_query(sql: str) -> bool:
    """Basic SQL validation (prevent injection, dangerous operations)"""
    sql_upper = sql.upper().strip()
    
    # Check for dangerous operations
    dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
    
    # Allow SELECT, WITH, EXPLAIN, etc.
    first_word = sql_upper.split()[0] if sql_upper.split() else ''
    
    if first_word not in ['SELECT', 'WITH', 'EXPLAIN', 'SHOW', 'DESCRIBE']:
        # Check if any dangerous keyword appears
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False
    
    return True

def format_sql(sql: str) -> str:
    """Basic SQL formatting"""
    # Remove extra whitespace
    sql = ' '.join(sql.split())
    
    # Add newlines for major keywords
    keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN']
    
    for keyword in keywords:
        sql = sql.replace(f' {keyword} ', f'\n{keyword} ')
    
    return sql