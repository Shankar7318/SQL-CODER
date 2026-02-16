import ollama
import logging

logger = logging.getLogger(__name__)

class SQLExplainer:
    def __init__(self, model_name: str = "sqlcoder:latest"):
        self.model_name = model_name
        self.client = None
        try:
            self.client = ollama.Client(host='http://127.0.0.1:11434')
            # Test connection
            self.client.list()
            logger.info(f"✅ SQLExplainer initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ollama client: {str(e)}")
            raise Exception(f"Cannot initialize Ollama client: {str(e)}")
    
    async def explain(self, sql_query: str) -> str:
        """Explain SQL query in plain English using SQLCoder"""
        try:
            if not self.client:
                raise Exception("Ollama client not available")
            
            prompt = self._build_explain_prompt(sql_query)
            logger.info(f"EXPLAIN PROMPT LENGTH: {len(prompt)}")
            
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 500,
                    "stop": ["\n\n", "```"]
                }
            )
            
            # Handle different response formats
            if hasattr(response, 'response'):
                explanation = response.response.strip()
            elif isinstance(response, dict) and 'response' in response:
                explanation = response['response'].strip()
            else:
                explanation = str(response).strip()
            
            logger.info(f"✅ Generated explanation for SQL")
            return explanation
            
        except Exception as e:
            logger.error(f"❌ SQL explanation failed: {str(e)}")
            raise Exception(f"SQL explanation failed: {str(e)}")

    def _build_explain_prompt(self, sql: str) -> str:
        """Build prompt for SQL explanation"""
        # Build the prompt as a regular string with explicit newlines
        prompt = "### Task\n"
        prompt += "Explain the following SQL query in simple, plain English:\n\n"
        prompt += "```sql\n"
        prompt += sql + "\n"
        prompt += "```\n\n"
        prompt += "### Instructions\n"
        prompt += "- Break down what the query does step by step\n"
        prompt += "- Explain any JOINs, WHERE conditions, GROUP BY, ORDER BY, etc.\n"
        prompt += "- Mention which tables are being queried\n"
        prompt += "- Explain what data is being retrieved\n"
        prompt += "- Keep it clear and concise for non-technical users\n"
        prompt += "- Do not include any markdown or code blocks in the response\n"
        prompt += "- Provide only the explanation, no additional text\n\n"
        prompt += "### Explanation\n"
        
        return prompt