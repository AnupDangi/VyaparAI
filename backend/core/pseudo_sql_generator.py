"""
Pseudo-SQL Generator - Generates simplified SQL structure from natural language
"""
import re
from typing import Dict, List, Any, Set
from backend.utils.llm_client import get_llm_client


class PseudoSQLGenerator:
    """Generates pseudo-SQL from natural language questions"""
    
    def __init__(self):
        self.llm = get_llm_client()
    
    def generate(self, question: str) -> Dict[str, Any]:
        """
        Generate pseudo-SQL from a natural language question
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with pseudo_sql, tables, and columns
        """
        system_prompt = """You are an expert at converting natural language questions into simplified SQL structure (pseudo-SQL).

Your task is to generate a pseudo-SQL query that captures the intent of the question without worrying about exact table/column names or database-specific syntax.

Rules:
1. Use generic but descriptive table names (e.g., customers, orders, products, employees, transactions)
2. Use generic but descriptive column names (e.g., customer_name, order_date, total_amount, created_at, price)
3. Include all relevant SQL operations: SELECT, FROM, WHERE, JOIN, GROUP BY, HAVING, ORDER BY, LIMIT
4. Handle temporal data naturally:
   - Use generic date columns: order_date, created_at, updated_at, transaction_date
   - Express date filters clearly: WHERE order_date >= '2024-01-01', YEAR(order_date) = 2024
   - Use date functions: DATE(), YEAR(), MONTH(), DAY(), DATE_DIFF(), NOW()
5. Handle numeric data and aggregations:
   - Use clear column names for money: price, amount, total_cost, salary
   - Include currency symbols in column names when relevant: price_usd, amount_eur
   - Use aggregation functions: SUM(), AVG(), COUNT(), MAX(), MIN()
6. Handle text and string operations:
   - Use LIKE for pattern matching: WHERE product_name LIKE '%phone%'
   - Use LOWER() or UPPER() for case-insensitive comparisons
7. Focus on query structure and logical flow, not exact syntax
8. Be concise, clear, and semantically accurate

Examples:

Example 1 - Basic aggregation with date range:
Question: "Show me top 10 customers by total purchase amount in 2024"
Pseudo-SQL: SELECT customer_name, SUM(purchase_amount) as total_spent FROM customers JOIN orders ON customers.customer_id = orders.customer_id WHERE YEAR(order_date) = 2024 GROUP BY customer_name ORDER BY total_spent DESC LIMIT 10

Example 2 - Date filtering with multiple conditions:
Question: "Find all orders placed in the last 30 days that cost more than $500"
Pseudo-SQL: SELECT order_id, customer_name, order_date, total_amount FROM orders JOIN customers ON orders.customer_id = customers.customer_id WHERE order_date >= DATE_SUB(NOW(), INTERVAL 30 DAY) AND total_amount > 500 ORDER BY order_date DESC

Example 3 - Time-based grouping:
Question: "What were our monthly sales totals for 2023?"
Pseudo-SQL: SELECT MONTH(order_date) as month, YEAR(order_date) as year, SUM(total_amount) as monthly_sales FROM orders WHERE YEAR(order_date) = 2023 GROUP BY YEAR(order_date), MONTH(order_date) ORDER BY month

Example 4 - Complex date comparison:
Question: "Show customers who haven't made a purchase in the last 6 months"
Pseudo-SQL: SELECT customer_id, customer_name, MAX(order_date) as last_order_date FROM customers LEFT JOIN orders ON customers.customer_id = orders.customer_id GROUP BY customer_id, customer_name HAVING MAX(order_date) < DATE_SUB(NOW(), INTERVAL 6 MONTH) OR MAX(order_date) IS NULL

Example 5 - Multiple joins with date and price filters:
Question: "List products with average rating above 4 stars that were sold more than 100 times last quarter"
Pseudo-SQL: SELECT product_id, product_name, AVG(rating) as avg_rating, COUNT(order_id) as times_sold, SUM(quantity * price) as total_revenue FROM products JOIN order_items ON products.product_id = order_items.product_id JOIN orders ON order_items.order_id = orders.order_id LEFT JOIN reviews ON products.product_id = reviews.product_id WHERE order_date >= DATE_SUB(NOW(), INTERVAL 3 MONTH) GROUP BY product_id, product_name HAVING AVG(rating) > 4 AND COUNT(order_id) > 100 ORDER BY total_revenue DESC

Now generate the pseudo-SQL for the following question:"""
        
        prompt = f"""Question: {question}

Generate pseudo-SQL for this question. Return ONLY the pseudo-SQL query, nothing else."""
        
        try:
            pseudo_sql = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.0
            )
            
            # Clean up the response
            pseudo_sql = self._clean_pseudo_sql(pseudo_sql)
            
            # Extract tables and columns
            tables = self._extract_tables(pseudo_sql)
            columns = self._extract_columns(pseudo_sql)
            
            return {
                "pseudo_sql": pseudo_sql,
                "tables": list(tables),
                "columns": list(columns),
                "original_question": question
            }
        
        except Exception as e:
            print(f"Error generating pseudo-SQL: {e}")
            return {
                "pseudo_sql": "",
                "tables": [],
                "columns": [],
                "original_question": question,
                "error": str(e)
            }
    
    def _clean_pseudo_sql(self, pseudo_sql: str) -> str:
        """Clean and format pseudo-SQL"""
        # Remove markdown code blocks
        pseudo_sql = re.sub(r'```sql\n?', '', pseudo_sql)
        pseudo_sql = re.sub(r'```\n?', '', pseudo_sql)
        
        # Remove extra whitespace
        pseudo_sql = ' '.join(pseudo_sql.split())
        
        # Remove semicolon at the end
        pseudo_sql = pseudo_sql.rstrip(';').strip()
        
        return pseudo_sql
    
    def _extract_tables(self, pseudo_sql: str) -> Set[str]:
        """Extract table names from pseudo-SQL"""
        tables = set()
        
        # Pattern: FROM table_name or JOIN table_name
        from_pattern = r'\bFROM\s+(\w+)'
        join_pattern = r'\bJOIN\s+(\w+)'
        
        from_matches = re.findall(from_pattern, pseudo_sql, re.IGNORECASE)
        join_matches = re.findall(join_pattern, pseudo_sql, re.IGNORECASE)
        
        tables.update(from_matches)
        tables.update(join_matches)
        
        return tables
    
    def _extract_columns(self, pseudo_sql: str) -> Set[str]:
        """Extract column names from pseudo-SQL"""
        columns = set()
        
        # Extract from SELECT clause
        select_pattern = r'\bSELECT\s+(.*?)\s+FROM'
        match = re.search(select_pattern, pseudo_sql, re.IGNORECASE | re.DOTALL)
        
        if match:
            select_clause = match.group(1)
            
            # Split by comma and extract column names
            parts = select_clause.split(',')
            for part in parts:
                # Remove aliases (AS alias_name)
                part = re.sub(r'\s+AS\s+\w+', '', part, flags=re.IGNORECASE)
                
                # Extract column name (handle table.column format)
                col_match = re.search(r'(\w+\.)?(\w+)', part.strip())
                if col_match:
                    col_name = col_match.group(2)
                    if col_name.upper() not in ['SELECT', 'FROM', 'WHERE', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN']:
                        columns.add(col_name)
        
        # Extract from WHERE clause
        where_pattern = r'\bWHERE\s+(.*?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)'
        match = re.search(where_pattern, pseudo_sql, re.IGNORECASE | re.DOTALL)
        
        if match:
            where_clause = match.group(1)
            # Extract column names from conditions
            col_matches = re.findall(r'(\w+\.)?(\w+)\s*[=<>!]', where_clause)
            for _, col_name in col_matches:
                if col_name.upper() not in ['AND', 'OR', 'NOT']:
                    columns.add(col_name)
        
        # Extract from GROUP BY
        group_pattern = r'\bGROUP\s+BY\s+(.*?)(?:\s+ORDER|\s+LIMIT|$)'
        match = re.search(group_pattern, pseudo_sql, re.IGNORECASE | re.DOTALL)
        
        if match:
            group_clause = match.group(1)
            parts = group_clause.split(',')
            for part in parts:
                col_match = re.search(r'(\w+\.)?(\w+)', part.strip())
                if col_match:
                    columns.add(col_match.group(2))
        
        # Extract from ORDER BY
        order_pattern = r'\bORDER\s+BY\s+(.*?)(?:\s+LIMIT|$)'
        match = re.search(order_pattern, pseudo_sql, re.IGNORECASE | re.DOTALL)
        
        if match:
            order_clause = match.group(1)
            parts = order_clause.split(',')
            for part in parts:
                # Remove ASC/DESC
                part = re.sub(r'\s+(ASC|DESC)', '', part, flags=re.IGNORECASE)
                col_match = re.search(r'(\w+\.)?(\w+)', part.strip())
                if col_match:
                    columns.add(col_match.group(2))
        
        return columns
