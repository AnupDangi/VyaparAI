"""
Schema Introspector - Extracts database schema metadata
"""
from typing import Dict, List, Any, Optional
from backend.utils.db_utils import get_db_manager


class SchemaIntrospector:
    """Introspects database schema and extracts metadata"""
    
    def __init__(self):
        self.db = get_db_manager()
        self._schema_cache = None
    
    def introspect(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Introspect database schema and return structured metadata
        
        Args:
            force_refresh: Force re-introspection even if cached
            
        Returns:
            Dictionary with schema metadata including tables, columns, types, constraints
        """
        if self._schema_cache and not force_refresh:
            return self._schema_cache
        
        schema = {
            "tables": {},
            "relationships": []
        }
        
        # Get all tables
        tables = self._get_tables()
        
        for table_name in tables:
            # Get columns for each table
            columns = self._get_columns(table_name)
            
            # Get primary keys
            primary_keys = self._get_primary_keys(table_name)
            
            # Get foreign keys
            foreign_keys = self._get_foreign_keys(table_name)
            
            schema["tables"][table_name] = {
                "name": table_name,
                "columns": columns,
                "primary_keys": primary_keys,
                "foreign_keys": foreign_keys,
                "description": self._generate_table_description(table_name, columns)
            }
        
        # Get relationships
        schema["relationships"] = self._get_relationships()
        
        self._schema_cache = schema
        return schema
    
    def _get_tables(self) -> List[str]:
        """Get all table names from the database"""
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        results = self.db.execute_query(query)
        return [row['table_name'] for row in results]
    
    def _get_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column metadata for a table"""
        query = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns
            WHERE table_schema = 'public' 
            AND table_name = %s
            ORDER BY ordinal_position
        """
        results = self.db.execute_query(query, (table_name,))
        
        columns = []
        for row in results:
            column = {
                "name": row['column_name'],
                "type": row['data_type'],
                "nullable": row['is_nullable'] == 'YES',
                "default": row['column_default'],
                "description": self._generate_column_description(
                    table_name, 
                    row['column_name'], 
                    row['data_type']
                )
            }
            
            # Add length/precision info if available
            if row['character_maximum_length']:
                column["max_length"] = row['character_maximum_length']
            if row['numeric_precision']:
                column["precision"] = row['numeric_precision']
            if row['numeric_scale']:
                column["scale"] = row['numeric_scale']
            
            columns.append(column)
        
        return columns
    
    def _get_primary_keys(self, table_name: str) -> List[str]:
        """Get primary key columns for a table"""
        query = """
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass
            AND i.indisprimary
        """
        results = self.db.execute_query(query, (table_name,))
        return [row['attname'] for row in results]
    
    def _get_foreign_keys(self, table_name: str) -> List[Dict[str, str]]:
        """Get foreign key constraints for a table"""
        query = """
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = %s
        """
        results = self.db.execute_query(query, (table_name,))
        
        foreign_keys = []
        for row in results:
            foreign_keys.append({
                "column": row['column_name'],
                "references_table": row['foreign_table_name'],
                "references_column": row['foreign_column_name']
            })
        
        return foreign_keys
    
    def _get_relationships(self) -> List[Dict[str, str]]:
        """Get all foreign key relationships in the database"""
        query = """
            SELECT
                tc.table_name AS from_table,
                kcu.column_name AS from_column,
                ccu.table_name AS to_table,
                ccu.column_name AS to_column
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
        """
        results = self.db.execute_query(query)
        
        relationships = []
        for row in results:
            relationships.append({
                "from_table": row['from_table'],
                "from_column": row['from_column'],
                "to_table": row['to_table'],
                "to_column": row['to_column']
            })
        
        return relationships
    
    def _generate_table_description(
        self, 
        table_name: str, 
        columns: List[Dict[str, Any]]
    ) -> str:
        """Generate a human-readable description for a table"""
        # Convert snake_case to Title Case
        readable_name = table_name.replace('_', ' ').title()
        
        # Get column names
        column_names = [col['name'] for col in columns[:5]]  # First 5 columns
        
        description = f"{readable_name} table"
        if column_names:
            description += f" with columns: {', '.join(column_names)}"
            if len(columns) > 5:
                description += f" and {len(columns) - 5} more"
        
        return description
    
    def _generate_column_description(
        self, 
        table_name: str, 
        column_name: str, 
        data_type: str
    ) -> str:
        """Generate a human-readable description for a column"""
        # Convert snake_case to readable format
        readable_name = column_name.replace('_', ' ').title()
        
        description = f"{readable_name} ({data_type})"
        
        # Add context based on common patterns
        if 'id' in column_name.lower():
            description += " - Identifier"
        elif 'name' in column_name.lower():
            description += " - Name field"
        elif 'date' in column_name.lower() or 'time' in column_name.lower():
            description += " - Date/Time field"
        elif 'amount' in column_name.lower() or 'price' in column_name.lower():
            description += " - Monetary value"
        elif 'email' in column_name.lower():
            description += " - Email address"
        elif 'phone' in column_name.lower():
            description += " - Phone number"
        
        return description
    
    def get_table_schema(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get schema for a specific table"""
        schema = self.introspect()
        return schema["tables"].get(table_name)
    
    def get_create_table_statement(self, table_name: str) -> str:
        """Generate CREATE TABLE statement for a table"""
        table_schema = self.get_table_schema(table_name)
        if not table_schema:
            return ""
        
        lines = [f"CREATE TABLE {table_name} ("]
        
        # Add columns
        column_defs = []
        for col in table_schema['columns']:
            col_def = f"  {col['name']} {col['type']}"
            if not col['nullable']:
                col_def += " NOT NULL"
            if col['default']:
                col_def += f" DEFAULT {col['default']}"
            column_defs.append(col_def)
        
        # Add primary keys
        if table_schema['primary_keys']:
            pk_def = f"  PRIMARY KEY ({', '.join(table_schema['primary_keys'])})"
            column_defs.append(pk_def)
        
        lines.append(',\n'.join(column_defs))
        lines.append(");")
        
        return '\n'.join(lines)
