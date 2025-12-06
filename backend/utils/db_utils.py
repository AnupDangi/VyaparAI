"""
Database utilities for connection management and safe query execution
"""
import os
import psycopg
from psycopg.rows import dict_row
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    """Manages database connections and query execution"""
    
    def __init__(self):
        self.conn_string = os.getenv("DATABASE_URL")
        if not self.conn_string:
            raise ValueError("DATABASE_URL not found in environment variables")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg.connect(self.conn_string, row_factory=dict_row)
            yield conn
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch_results: bool = True,
        timeout: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query safely with timeout
        
        Args:
            query: SQL query to execute
            params: Query parameters (for parameterized queries)
            fetch_results: Whether to fetch and return results
            timeout: Query timeout in seconds
            
        Returns:
            List of result rows as dictionaries
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Set statement timeout
                cur.execute(f"SET statement_timeout = {timeout * 1000}")
                
                # Execute query
                if params:
                    cur.execute(query, params)
                else:
                    cur.execute(query)
                
                if fetch_results:
                    return cur.fetchall()
                
                conn.commit()
                return []
    
    def execute_query_safe(
        self,
        query: str,
        max_rows: int = 100
    ) -> Dict[str, Any]:
        """
        Execute query with safety checks and return results with metadata
        
        Args:
            query: SQL query to execute
            max_rows: Maximum number of rows to return
            
        Returns:
            Dictionary with results, error (if any), and metadata
        """
        result = {
            "success": False,
            "results": [],
            "error": None,
            "row_count": 0,
            "column_names": []
        }
        
        try:
            # Add LIMIT if not present
            query_upper = query.upper().strip()
            if "LIMIT" not in query_upper:
                query = f"{query.rstrip(';')} LIMIT {max_rows}"
            
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Set timeout
                    cur.execute("SET statement_timeout = 30000")
                    
                    # Execute query
                    cur.execute(query)
                    
                    # Fetch results
                    results = cur.fetchall()
                    
                    result["success"] = True
                    result["results"] = results
                    result["row_count"] = len(results)
                    
                    if results:
                        result["column_names"] = list(results[0].keys())
        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def get_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """
        results = self.execute_query(query)
        return [row['table_name'] for row in results]


# Global instance
_db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get or create global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
