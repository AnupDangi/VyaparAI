"""
SQL Debugger - Executes SQL and fixes errors using LLM
"""
import os
from typing import Dict, Any, Optional
from backend.utils.llm_client import get_llm_client
from backend.utils.db_utils import get_db_manager
from dotenv import load_dotenv

load_dotenv()


class SQLDebugger:
    """Debugs and fixes SQL queries"""
    
    def __init__(self):
        self.llm = get_llm_client()
        self.db = get_db_manager()
        self.max_retries = int(os.getenv("MAX_DEBUG_RETRIES", "3"))
    
    def execute_and_debug(
        self,
        sql: str,
        original_question: str,
        schema_context: str,
        max_retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute SQL and debug if errors occur
        
        Args:
            sql: SQL query to execute
            original_question: Original natural language question
            schema_context: Schema information for context
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary with results, final SQL, and debugging info
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        current_sql = sql
        debug_history = []
        
        for attempt in range(max_retries + 1):
            # Execute the query
            result = self.db.execute_query_safe(current_sql)
            
            if result['success']:
                return {
                    "success": True,
                    "sql": current_sql,
                    "results": result['results'],
                    "row_count": result['row_count'],
                    "column_names": result['column_names'],
                    "attempts": attempt + 1,
                    "debug_history": debug_history
                }
            
            # If failed and we have retries left, try to fix
            if attempt < max_retries:
                debug_info = {
                    "attempt": attempt + 1,
                    "failed_sql": current_sql,
                    "error": result['error']
                }
                
                # Try to fix the SQL
                fixed_result = self._fix_sql(
                    current_sql,
                    result['error'],
                    original_question,
                    schema_context
                )
                
                if fixed_result['success']:
                    current_sql = fixed_result['sql']
                    debug_info['fixed_sql'] = current_sql
                    debug_history.append(debug_info)
                else:
                    # Can't fix, return error
                    debug_info['fix_failed'] = True
                    debug_history.append(debug_info)
                    break
            else:
                # Out of retries
                debug_history.append({
                    "attempt": attempt + 1,
                    "failed_sql": current_sql,
                    "error": result['error'],
                    "out_of_retries": True
                })
        
        # All attempts failed
        return {
            "success": False,
            "sql": current_sql,
            "results": [],
            "row_count": 0,
            "column_names": [],
            "error": result['error'],
            "attempts": len(debug_history),
            "debug_history": debug_history
        }
    
    def _fix_sql(
        self,
        sql: str,
        error: str,
        original_question: str,
        schema_context: str
    ) -> Dict[str, Any]:
        """
        Use LLM to fix SQL based on error message
        
        Args:
            sql: Failed SQL query
            error: Error message from database
            original_question: Original question for context
            schema_context: Schema information
            
        Returns:
            Dictionary with fixed SQL or error
        """
        system_prompt = """You are an expert PostgreSQL debugger. Fix SQL queries based on error messages.

Rules:
1. Analyze the error message carefully
2. Fix ONLY the specific issue causing the error
3. Maintain the original query intent
4. Use the provided schema to ensure correctness
5. Return ONLY the corrected SQL query, no explanations
6. Do NOT use markdown code blocks"""
        
        prompt = f"""Original Question: {original_question}

Schema Context:
{schema_context}

Failed SQL Query:
{sql}

Error Message:
{error}

Fix the SQL query to resolve this error. Return ONLY the corrected SQL:"""
        
        try:
            fixed_sql = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.0
            )
            
            # Clean the SQL
            fixed_sql = self._clean_sql(fixed_sql)
            
            return {
                "success": True,
                "sql": fixed_sql
            }
        
        except Exception as e:
            print(f"Error fixing SQL: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _clean_sql(self, sql: str) -> str:
        """Clean SQL query"""
        import re
        
        # Remove markdown code blocks
        sql = re.sub(r'```sql\n?', '', sql)
        sql = re.sub(r'```\n?', '', sql)
        
        # Remove extra whitespace
        lines = [line.strip() for line in sql.split('\n') if line.strip()]
        sql = '\n'.join(lines)
        
        # Ensure semicolon
        if not sql.endswith(';'):
            sql += ';'
        
        return sql
