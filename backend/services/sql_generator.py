import ollama
import logging
from typing import Optional, List, Dict, Any
import re
import json

logger = logging.getLogger(__name__)

class SQLGenerator:
    def __init__(self, model_name: str = "sqlcoder:latest"):
        self.model_name = model_name
        self.client = None
        try:
            self.client = ollama.Client(host='http://localhost:11434')
            models = self.client.list()
            logger.info(f"✅ Connected to Ollama successfully")
            
            if hasattr(models, 'models'):
                model_names = [m.model for m in models.models]
                logger.info(f"Available models: {model_names}")
                if self.model_name in model_names:
                    logger.info(f"✅ Model {self.model_name} is available")
                else:
                    logger.warning(f"⚠️ Model {self.model_name} not found. Available: {model_names}")
            else:
                logger.warning(f"Unexpected response format: {type(models)}")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ollama client: {str(e)}")
            raise Exception(f"Cannot initialize Ollama client: {str(e)}")
    
    async def generate(self, natural_language_query: str, schema: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Convert natural language to SQL - Works with ANY database
        Step 1: Analyze schema
        Step 2: Understand query intent
        Step 3: Generate SQL
        """
        try:
            if not self.client:
                raise Exception("Ollama client not available")
            
            # STEP 1: ANALYZE SCHEMA - Understand the database structure
            if not schema:
                logger.warning("No schema provided!")
                return self._get_fallback_query(natural_language_query)
            
            logger.info(f"📊 Analyzing schema with {len(schema)} tables")
            analysis = self._analyze_schema(schema)
            
            # STEP 2: UNDERSTAND QUERY INTENT - What is the user asking?
            intent = self._analyze_intent(natural_language_query, analysis)
            logger.info(f"🎯 Query intent: {intent['type']}")
            
            # STEP 3: BUILD INTELLIGENT PROMPT with schema context
            prompt = self._build_prompt(natural_language_query, analysis, intent)
            logger.info(f"📝 Prompt length: {len(prompt)}")
            
            # STEP 4: GENERATE SQL using Ollama
            logger.info("🤖 Sending request to Ollama...")
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "max_tokens": 500,
                    "stop": ["\n\n", "```", ";"]
                }
            )
            
            # Extract and clean SQL
            raw_response = self._extract_response(response)
            sql = self._clean_sql(raw_response)
            logger.info(f"✅ Generated SQL: {sql[:100]}...")
            
            # Validate and format
            if not self._validate_sql(sql):
                logger.warning("⚠️ Generated SQL invalid, using fallback")
                sql = self._get_intelligent_fallback(natural_language_query, analysis, intent)
            
            return self._format_sql(sql)
            
        except Exception as e:
            logger.error(f"❌ SQL generation failed: {str(e)}")
            return self._get_fallback_query(natural_language_query)
    
    def _analyze_schema(self, schema: List[Dict[str, Any]]) -> Dict:
        """
        Deeply analyze ANY database schema to understand:
        - Tables and their purposes
        - Columns and their data types
        - Relationships between tables
        - Which columns are metrics vs dimensions
        """
        analysis = {
            "tables": [],
            "relationships": [],
            "table_summary": {},
            "metrics": {},  # Numeric columns that could be aggregated
            "dimensions": {},  # Text columns that could be used for grouping
            "dates": {},  # Date columns for time-based queries
            "ids": {},  # ID columns for joins
            "names": {},  # Name columns for labels
        }
        
        for table in schema:
            if not isinstance(table, dict):
                continue
            
            table_name = table.get('name') or table.get('table_name', 'unknown')
            columns = table.get('columns', [])
            
            # Analyze table purpose based on name
            table_type = self._classify_table(table_name)
            
            table_info = {
                "name": table_name,
                "type": table_type,
                "columns": [],
                "primary_keys": [],
                "foreign_keys": []
            }
            
            # Track different column types
            metrics = []
            dimensions = []
            dates = []
            ids = []
            names = []
            
            for col in columns:
                if not isinstance(col, dict):
                    continue
                
                col_name = col.get('name') or col.get('column_name', 'unknown')
                col_type = col.get('type') or col.get('data_type', 'unknown').lower()
                is_primary = col.get('isPrimary', False)
                
                col_info = {
                    "name": col_name,
                    "type": col_type,
                    "is_primary": is_primary,
                    "semantic": self._classify_column(col_name, col_type)
                }
                table_info["columns"].append(col_info)
                
                # Track primary keys
                if is_primary:
                    table_info["primary_keys"].append(col_name)
                    ids.append(col_name)
                
                # Classify by data type and name
                if any(t in col_type for t in ['int', 'decimal', 'numeric', 'float', 'double']):
                    # This is a numeric column - potential metric
                    metrics.append(col_name)
                    
                    # Check if it might be a salary/wage column
                    if any(term in col_name.lower() for term in ['salary', 'wage', 'income', 'pay']):
                        col_info["semantic"] = "salary"
                
                elif any(t in col_type for t in ['char', 'text', 'varchar']):
                    # This is a text column - potential dimension
                    dimensions.append(col_name)
                    
                    # Check if it's a name field
                    if any(term in col_name.lower() for term in ['name', 'first_name', 'last_name']):
                        names.append(col_name)
                        col_info["semantic"] = "name"
                
                elif any(t in col_type for t in ['date', 'time', 'timestamp']):
                    dates.append(col_name)
                    col_info["semantic"] = "date"
                
                # Detect foreign keys
                if ('id' in col_name.lower() and not is_primary) or col_name.lower().endswith('_id'):
                    table_info["foreign_keys"].append(col_name)
                    ids.append(col_name)
            
            # Store column classifications
            analysis["metrics"][table_name] = metrics
            analysis["dimensions"][table_name] = dimensions
            analysis["dates"][table_name] = dates
            analysis["ids"][table_name] = ids
            analysis["names"][table_name] = names
            
            analysis["tables"].append(table_info)
            analysis["table_summary"][table_name] = {
                "type": table_type,
                "column_count": len(columns),
                "has_metrics": len(metrics) > 0,
                "has_dimensions": len(dimensions) > 0,
                "has_dates": len(dates) > 0
            }
        
        # Detect relationships between tables
        self._detect_relationships(analysis)
        
        logger.info(f"Schema analysis complete: {len(analysis['tables'])} tables, {len(analysis['relationships'])} relationships")
        return analysis
    
    def _classify_table(self, table_name: str) -> str:
        """Classify table purpose based on name"""
        name = table_name.lower()
        
        if any(word in name for word in ['user', 'customer', 'client', 'person']):
            return "entity: people"
        elif any(word in name for word in ['product', 'item', 'goods']):
            return "entity: products"
        elif any(word in name for word in ['order', 'purchase', 'sale', 'transaction']):
            return "transaction: orders"
        elif any(word in name for word in ['employee', 'staff', 'worker']):
            return "entity: employees"
        elif any(word in name for word in ['department', 'team']):
            return "organization: departments"
        elif any(word in name for word in ['category', 'type']):
            return "lookup: categories"
        elif any(word in name for word in ['address', 'location']):
            return "lookup: locations"
        elif any(word in name for word in ['review', 'rating']):
            return "activity: reviews"
        else:
            return "data: general"
    
    def _classify_column(self, column_name: str, column_type: str) -> str:
        """Classify column purpose based on name and type"""
        name = column_name.lower()
        
        # ID columns
        if name == 'id' or name.endswith('_id'):
            return "identifier"
        
        # Name columns
        if any(word in name for word in ['name', 'first_name', 'last_name']):
            return "name"
        
        # Date columns
        if any(word in name for word in ['date', 'time', 'created', 'updated']):
            return "date"
        
        # Status/Type columns
        if any(word in name for word in ['status', 'type', 'category']):
            return "category"
        
        # Metric columns
        if any(t in column_type for t in ['int', 'decimal', 'numeric']):
            if any(word in name for word in ['price', 'cost', 'amount', 'salary', 'wage']):
                return "metric"
            return "number"
        
        return "attribute"
    
    def _detect_relationships(self, analysis: Dict) -> None:
        """Detect relationships between tables based on column names"""
        id_map = {}
        
        # Build map of ID columns
        for table_name, ids in analysis["ids"].items():
            for id_col in ids:
                id_map[f"{table_name}.{id_col}"] = table_name
        
        # Look for foreign key relationships
        for table_info in analysis["tables"]:
            for fk_col in table_info["foreign_keys"]:
                fk_base = fk_col.lower().replace('_id', '').replace('id', '')
                
                # Try to find matching table
                for other_table in analysis["tables"]:
                    if other_table["name"] == table_info["name"]:
                        continue
                    
                    # Check if this could be the referenced table
                    if fk_base in other_table["name"].lower() or other_table["name"].lower() in fk_base:
                        # Find the primary key of the other table
                        if other_table["primary_keys"]:
                            analysis["relationships"].append({
                                "from_table": table_info["name"],
                                "from_column": fk_col,
                                "to_table": other_table["name"],
                                "to_column": other_table["primary_keys"][0]
                            })
                            break
    
    def _analyze_intent(self, query: str, analysis: Dict) -> Dict:
        """Understand what the user is asking for"""
        query_lower = query.lower()
        words = query_lower.split()
        
        intent = {
            "type": "select",
            "needs_aggregation": False,
            "needs_filtering": False,
            "needs_grouping": False,
            "needs_sorting": False,
            "needs_joining": False,
            "target_tables": [],
            "target_columns": [],
            "aggregation_type": None,
            "filter_conditions": [],
            "sort_order": None
        }
        
        # Check for aggregation keywords
        if any(word in query_lower for word in ['total', 'sum', 'average', 'avg', 'count', 'maximum', 'minimum', 'max', 'min']):
            intent["needs_aggregation"] = True
            
            if 'sum' in query_lower or 'total' in query_lower:
                intent["aggregation_type"] = "SUM"
            elif 'average' in query_lower or 'avg' in query_lower:
                intent["aggregation_type"] = "AVG"
            elif 'count' in query_lower:
                intent["aggregation_type"] = "COUNT"
            elif 'maximum' in query_lower or 'max' in query_lower:
                intent["aggregation_type"] = "MAX"
            elif 'minimum' in query_lower or 'min' in query_lower:
                intent["aggregation_type"] = "MIN"
        
        # Check for filtering
        if any(word in query_lower for word in ['where', 'with', 'having', 'greater', 'less', 'than', 'above', 'below', 'between']):
            intent["needs_filtering"] = True
        
        # Check for grouping
        if any(word in query_lower for word in ['group', 'by', 'each', 'per', 'category']):
            intent["needs_grouping"] = True
        
        # Check for sorting
        if any(word in query_lower for word in ['top', 'best', 'worst', 'highest', 'lowest', 'order', 'sort', 'limit']):
            intent["needs_sorting"] = True
            if 'top' in query_lower or 'best' in query_lower or 'highest' in query_lower:
                intent["sort_order"] = "DESC"
            elif 'worst' in query_lower or 'lowest' in query_lower:
                intent["sort_order"] = "ASC"
        
        # Check for joins
        if any(word in query_lower for word in ['with', 'and', 'together', 'join', 'combined']):
            intent["needs_joining"] = True
        
        # Find relevant tables based on keywords
        for table_info in analysis["tables"]:
            table_name = table_info["name"].lower()
            for word in words:
                if len(word) > 3 and (word in table_name or table_name in word):
                    intent["target_tables"].append(table_info["name"])
                    break
        
        # Special handling for salary/employee queries
        if any(word in query_lower for word in ['salary', 'wage', 'income', 'pay']):
            intent["type"] = "salary_analysis"
            intent["needs_filtering"] = True
            
            # Find employee table and salary column
            for table_name, metrics in analysis["metrics"].items():
                if any(term in table_name.lower() for term in ['user', 'employee', 'staff']):
                    intent["target_tables"].append(table_name)
                    
                    # Find salary column
                    for metric in metrics:
                        if any(term in metric.lower() for term in ['salary', 'wage', 'income']):
                            intent["salary_column"] = f"{table_name}.{metric}"
                            break
        
        return intent
    
    def _build_prompt(self, query: str, analysis: Dict, intent: Dict) -> str:
        """Build an intelligent prompt with schema context"""
        
        prompt = "### Task\n"
        prompt += f"Generate a SQL query to answer: {query}\n\n"
        
        # DATABASE SCHEMA SECTION
        prompt += "### Database Schema (USE EXACT NAMES):\n\n"
        
        for table_info in analysis["tables"]:
            table_name = table_info["name"]
            prompt += f"Table: {table_name} ({table_info['type']})\n"
            prompt += "Columns:\n"
            
            for col in table_info["columns"]:
                prompt += f"  - {col['name']} ({col['type']})"
                if col['is_primary']:
                    prompt += " PRIMARY KEY"
                prompt += f"  # {col['semantic']}\n"
            
            # Show important columns
            if analysis["metrics"].get(table_name):
                prompt += f"  Numeric columns: {', '.join(analysis['metrics'][table_name][:3])}\n"
            if analysis["dimensions"].get(table_name):
                prompt += f"  Text columns: {', '.join(analysis['dimensions'][table_name][:3])}\n"
            if analysis["dates"].get(table_name):
                prompt += f"  Date columns: {', '.join(analysis['dates'][table_name][:3])}\n"
            
            prompt += "\n"
        
        # RELATIONSHIPS SECTION
        if analysis["relationships"]:
            prompt += "### Relationships:\n"
            for rel in analysis["relationships"][:5]:
                prompt += f"- {rel['from_table']}.{rel['from_column']} = {rel['to_table']}.{rel['to_column']}\n"
            prompt += "\n"
        
        # QUERY ANALYSIS SECTION
        prompt += "### Query Analysis:\n"
        
        if intent["target_tables"]:
            prompt += f"- Relevant tables: {', '.join(intent['target_tables'][:3])}\n"
        
        if intent["needs_aggregation"]:
            prompt += f"- Needs {intent['aggregation_type'] or 'aggregation'}\n"
            
            # Suggest metric columns
            all_metrics = []
            for table in intent["target_tables"] or analysis["tables"][:2]:
                if isinstance(table, dict):
                    table_name = table.get("name")
                else:
                    table_name = table
                if table_name and analysis["metrics"].get(table_name):
                    all_metrics.extend([f"{table_name}.{m}" for m in analysis["metrics"][table_name][:2]])
            
            if all_metrics:
                prompt += f"  Available metrics: {', '.join(all_metrics[:3])}\n"
        
        if intent["needs_grouping"]:
            prompt += "- Needs GROUP BY\n"
            
            # Suggest dimension columns
            all_dims = []
            for table in intent["target_tables"] or analysis["tables"][:2]:
                if isinstance(table, dict):
                    table_name = table.get("name")
                else:
                    table_name = table
                if table_name and analysis["dimensions"].get(table_name):
                    all_dims.extend([f"{table_name}.{d}" for d in analysis["dimensions"][table_name][:2]])
                if table_name and analysis["names"].get(table_name):
                    all_dims.extend([f"{table_name}.{n}" for n in analysis["names"][table_name][:2]])
            
            if all_dims:
                prompt += f"  Possible grouping columns: {', '.join(all_dims[:3])}\n"
        
        if intent["needs_filtering"]:
            prompt += "- Needs WHERE clause filtering\n"
        
        if intent["needs_sorting"]:
            prompt += f"- Needs ORDER BY {intent['sort_order'] or 'DESC'} and LIMIT\n"
        
        if intent["needs_joining"] and analysis["relationships"]:
            prompt += "- Needs JOIN using relationships above\n"
        
        # SPECIAL HANDLING FOR SALARY QUERIES
        if intent["type"] == "salary_analysis":
            prompt += "\n### Salary Query Instructions:\n"
            prompt += "- This query asks about salary above average\n"
            prompt += "- Use a subquery to calculate average salary\n"
            prompt += "- Format: SELECT columns FROM table WHERE salary > (SELECT AVG(salary) FROM table)\n"
            
            if intent.get("salary_column"):
                prompt += f"- Use salary column: {intent['salary_column']}\n"
            
            # Find name columns
            for table in intent["target_tables"]:
                if analysis["names"].get(table):
                    prompt += f"- Include name columns: {', '.join(analysis['names'][table][:2])}\n"
        
        prompt += "\n### Instructions:\n"
        prompt += "1. Use ONLY table and column names from the schema above\n"
        prompt += "2. Return ONLY the SQL query, no explanations\n"
        prompt += "3. End with a semicolon\n"
        prompt += "4. Do NOT include markdown or tags\n\n"
        
        prompt += "### SQL Query:\n"
        
        return prompt
    
    def _extract_response(self, response) -> str:
        """Extract response from Ollama in any format"""
        if hasattr(response, 'response'):
            return response.response
        elif isinstance(response, dict) and 'response' in response:
            return response['response']
        else:
            return str(response)
    
    def _clean_sql(self, sql: str) -> str:
        """Clean up generated SQL"""
        if not sql:
            return ""
        
        # Remove tags and markdown
        sql = sql.replace('<s>', '').replace('</s>', '').strip()
        sql = re.sub(r'```sql\s*', '', sql)
        sql = re.sub(r'```\s*', '', sql)
        
        # Remove comments
        sql = re.sub(r'^#.*?\n', '', sql)
        
        # Take first statement
        statements = sql.split(';')
        if statements:
            sql = statements[0].strip() + ';'
        
        return sql
    
    def _format_sql(self, sql: str) -> str:
        """Format SQL for readability"""
        if not sql:
            return sql
        
        # Add line breaks after keywords
        keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING', 'JOIN', 
                    'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN', 'LIMIT']
        
        for keyword in keywords:
            sql = sql.replace(f' {keyword} ', f'\n{keyword} ')
        
        # Handle commas in SELECT
        if 'SELECT' in sql:
            parts = sql.split('\nSELECT ')
            if len(parts) > 1:
                select_part = parts[1].split('\nFROM')[0]
                if ',' in select_part:
                    formatted = select_part.replace(', ', ',\n    ')
                    sql = sql.replace(select_part, formatted)
        
        return sql
    
    def _validate_sql(self, sql: str) -> bool:
        """Basic SQL validation"""
        if not sql or len(sql) < 10:
            return False
        
        sql_upper = sql.upper()
        valid_starts = ['SELECT', 'WITH', 'SHOW']
        
        return any(sql_upper.startswith(word) for word in valid_starts)
    
    def _get_intelligent_fallback(self, query: str, analysis: Dict, intent: Dict) -> str:
        """Intelligent fallback based on schema analysis"""
        query_lower = query.lower()
        
        # Handle salary queries
        if 'salary' in query_lower or 'wage' in query_lower:
            # Find employee table and salary column
            for table_name, metrics in analysis["metrics"].items():
                if any(term in table_name.lower() for term in ['user', 'employee', 'staff']):
                    # Find salary column
                    salary_col = None
                    for metric in metrics:
                        if any(term in metric.lower() for term in ['salary', 'wage', 'income']):
                            salary_col = metric
                            break
                    
                    if salary_col:
                        # Find name columns
                        name_cols = analysis["names"].get(table_name, ['first_name', 'last_name'])[:2]
                        name_select = ', '.join(name_cols) if name_cols else '*'
                        
                        return f"""
SELECT 
    {name_select},
    {salary_col}
FROM {table_name}
WHERE {salary_col} > (SELECT AVG({salary_col}) FROM {table_name})
ORDER BY {salary_col} DESC;
"""
        
        # Generic fallback
        if intent["target_tables"]:
            table = intent["target_tables"][0]
        else:
            table = analysis["tables"][0]["name"] if analysis["tables"] else "users"
        
        return f"SELECT * FROM {table} LIMIT 10;"
    
    def _get_fallback_query(self, query: str) -> str:
        """Ultimate fallback"""
        return "SELECT 1;"
    
    async def check_availability(self) -> bool:
        """Check if Ollama is available"""
        return self.client is not None