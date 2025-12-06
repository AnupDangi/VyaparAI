"""
SQL Generator - Generates executable SQL from natural language with grounded schema
"""
import re
from typing import Dict, Any, Optional
from backend.utils.llm_client import get_llm_client
from backend.core.schema_introspector import SchemaIntrospector


class SQLGenerator:
    """Generates SQL queries from natural language"""
    
    def __init__(self):
        self.llm = get_llm_client()
        self.schema_introspector = SchemaIntrospector()
    
    def generate(
        self,
        question: str,
        grounded_schema: Dict[str, Any],
        pseudo_sql: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate SQL query from natural language question
        
        Args:
            question: Natural language question
            grounded_schema: Relevant schema subset
            pseudo_sql: Optional pseudo-SQL for guidance
            
        Returns:
            Dictionary with generated SQL and metadata
        """
        # Build comprehensive prompt
        prompt = self._build_prompt(question, grounded_schema, pseudo_sql)
        
        # Detect if user specified a specific count/limit
        has_explicit_limit = self._has_explicit_limit(question)
        limit_instruction = "" if has_explicit_limit else "\n9. IMPORTANT: If the query returns multiple rows (uses GROUP BY or lists items), add 'LIMIT 5' to keep results concise unless the user specified a different number"
        
        system_prompt = f"""You are an expert PostgreSQL developer. Generate accurate, efficient SQL queries based on the provided schema.

Rules:
1. Use ONLY the tables and columns provided in the schema
2. Generate valid PostgreSQL syntax
3. Use proper JOINs when querying multiple tables
4. Include appropriate WHERE clauses, GROUP BY, ORDER BY as needed
5. Be mindful of NULL values and use appropriate handling
6. Return ONLY the SQL query, no explanations
7. Do NOT use markdown code blocks, return raw SQL
8. Ensure all column references are unambiguous (use table aliases if needed)
9. IMPORTANT: For text comparisons (city names, customer names, product names, etc.), ALWAYS use ILIKE with wildcards for case-insensitive partial matching
   Example: WHERE city ILIKE '%new york%' instead of WHERE city = 'New York'
   This will match 'New York', 'New York City', 'NEW YORK CITY', etc.{limit_instruction}"""
        
        try:
            sql_query = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.0,
                max_tokens=1024
            )
            
            # Clean the SQL
            sql_query = self._clean_sql(sql_query)
            
            return {
                "sql": sql_query,
                "success": True,
                "error": None
            }
        
        except Exception as e:
            print(f"Error generating SQL: {e}")
            return {
                "sql": "",
                "success": False,
                "error": str(e)
            }
    
    def _build_prompt(
        self,
        question: str,
        grounded_schema: Dict[str, Any],
        pseudo_sql: Optional[str] = None
    ) -> str:
        """Build comprehensive prompt for SQL generation"""
        prompt_parts = []
        
        # Add CREATE TABLE statements
        prompt_parts.append("Database Schema (PostgreSQL):")
        prompt_parts.append("=" * 60)
        
        for table_name in grounded_schema['tables'].keys():
            create_stmt = self.schema_introspector.get_create_table_statement(table_name)
            if create_stmt:
                prompt_parts.append(create_stmt)
                prompt_parts.append("")
        
        # Add relationships if any
        if grounded_schema.get('relationships'):
            prompt_parts.append("\nRelationships:")
            for rel in grounded_schema['relationships']:
                prompt_parts.append(
                    f"  {rel['from_table']}.{rel['from_column']} -> "
                    f"{rel['to_table']}.{rel['to_column']}"
                )
            prompt_parts.append("")
        
        # Add few-shot examples
        prompt_parts.append(self._get_few_shot_examples())
        
        # Add pseudo-SQL if available
        if pseudo_sql:
            prompt_parts.append(f"\nReference Structure (Pseudo-SQL):")
            prompt_parts.append(pseudo_sql)
            prompt_parts.append("")
        
        # Add the question
        prompt_parts.append("=" * 60)
        prompt_parts.append(f"Question: {question}")
        prompt_parts.append("\nGenerate the SQL query:")
        
        return '\n'.join(prompt_parts)
    
    def _get_few_shot_examples(self) -> str:
        """Get few-shot examples for SQL generation"""
        examples = """
Examples:

Question: Show me all customers
SQL: SELECT * FROM customers;

Question: Count total orders
SQL: SELECT COUNT(*) as total_orders FROM orders;

Question: Get top 5 products by price
SQL: SELECT * FROM products ORDER BY price DESC LIMIT 5;

Question: Find customers who placed orders in 2024
SQL: SELECT DISTINCT c.* FROM customers c JOIN orders o ON c.id = o.customer_id WHERE EXTRACT(YEAR FROM o.order_date) = 2024;

Question: Calculate total sales per customer
SQL: SELECT c.customer_name, SUM(o.total_amount) as total_sales FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id, c.customer_name ORDER BY total_sales DESC;
"""
        return examples
    
    def _has_explicit_limit(self, question: str) -> bool:
        """Check if question explicitly mentions a count/limit"""
        question_lower = question.lower()
        
        # Check for explicit numbers (top 10, first 20, etc.)
        import re
        number_patterns = [
            r'top\s+\d+',
            r'first\s+\d+',
            r'last\s+\d+',
            r'\d+\s+(?:customers|products|orders|items|rows|results)',
            r'limit\s+\d+',
        ]
        
        for pattern in number_patterns:
            if re.search(pattern, question_lower):
                return True
        
        # Check for "all" which means no limit
        if 'all' in question_lower or 'every' in question_lower:
            return True
        
        return False
    
    def _clean_sql(self, sql: str) -> str:
        """Clean and format SQL query"""
        # Remove markdown code blocks
        sql = re.sub(r'```sql\n?', '', sql)
        sql = re.sub(r'```\n?', '', sql)
        
        # Remove markdown or extra formatting
        sql = re.sub(r'^SQL:\s*', '', sql, flags=re.IGNORECASE)
        
        # Remove extra whitespace but preserve line breaks for readability
        lines = [line.strip() for line in sql.split('\n') if line.strip()]
        sql = '\n'.join(lines)
        
        # Ensure it ends with semicolon
        if not sql.endswith(';'):
            sql += ';'
        
        return sql
