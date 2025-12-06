"""
Schema Retriever - Retrieves relevant schema using vector similarity
"""
import os
from typing import Dict, List, Any, Set
from collections import defaultdict
from backend.core.embedding_manager import get_embedding_manager
from dotenv import load_dotenv

load_dotenv()


class SchemaRetriever:
    """Retrieves relevant schema elements using vector similarity"""
    
    def __init__(self):
        self.embedding_manager = get_embedding_manager()
        self.top_k_columns = int(os.getenv("TOP_K_COLUMNS", "20"))
        self.top_k_tables = int(os.getenv("TOP_K_TABLES", "5"))
    
    def retrieve_schema(
        self, 
        question: str,
        pseudo_sql_info: Dict[str, Any],
        full_schema: Dict[str, Any],
        top_k_columns: int = None,
        top_k_tables: int = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant schema elements using progressive pruning
        
        Args:
            question: Natural language question
            pseudo_sql_info: Pseudo-SQL information with tables/columns
            full_schema: Full database schema
            top_k_columns: Number of top columns to retrieve
            top_k_tables: Number of top tables to keep
            
        Returns:
            Grounded schema with only relevant tables and columns
        """
        if top_k_columns is None:
            top_k_columns = self.top_k_columns
        if top_k_tables is None:
            top_k_tables = self.top_k_tables
        
        # Step 1: Column-level vector search using Q_enriched (Gen-SQL Step 2.2)
        search_query = self._create_search_query(question, pseudo_sql_info)
        
        # Print Q_enriched for debugging
        print(f"  💡 Q_enriched:\n{search_query}\n")
        
        column_results = self.embedding_manager.search(search_query, top_k=top_k_columns)
        
        # Step 2: Aggregate scores by table
        table_scores = self._aggregate_table_scores(column_results)
        
        # Step 3: Select top tables
        top_tables = self._select_top_tables(table_scores, top_k_tables)
        
        # Step 4: Build grounded schema
        grounded_schema = self._build_grounded_schema(
            column_results,
            top_tables,
            full_schema
        )
        
        return grounded_schema
    
    def _create_search_query(
        self, 
        question: str, 
        pseudo_sql_info: Dict[str, Any]
    ) -> str:
        """
        Create Q_enriched: enriched query text combining question, pseudo-schema, and pseudo-SQL
        This follows the Gen-SQL architecture (Step 2.2)
        """
        parts = []
        
        # Part 1: Original question
        parts.append(f"Question: {question}")
        
        # Part 2: Linearized pseudo-schema
        pseudo_schema_parts = []
        
        # Add pseudo tables
        if pseudo_sql_info.get('tables'):
            tables_str = ', '.join(pseudo_sql_info['tables'])
            pseudo_schema_parts.append(f"Pseudo tables: {tables_str}")
        
        # Add pseudo columns
        if pseudo_sql_info.get('columns'):
            columns_str = ', '.join(pseudo_sql_info['columns'])
            pseudo_schema_parts.append(f"Pseudo columns: {columns_str}")
        
        if pseudo_schema_parts:
            parts.append(' | '.join(pseudo_schema_parts))
        
        # Part 3: Pseudo-SQL itself (helps with semantic understanding)
        if pseudo_sql_info.get('pseudo_sql'):
            parts.append(f"Pseudo SQL: {pseudo_sql_info['pseudo_sql']}")
        
        # Combine all parts into Q_enriched
        q_enriched = '\n'.join(parts)
        
        return q_enriched
    
    def _aggregate_table_scores(
        self, 
        column_results: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Aggregate similarity scores by table"""
        table_scores = defaultdict(float)
        table_counts = defaultdict(int)
        
        for result in column_results:
            table_name = result['metadata']['table']
            similarity = result['similarity']
            
            # Accumulate scores
            table_scores[table_name] += similarity
            table_counts[table_name] += 1
        
        # Calculate average scores
        avg_scores = {}
        for table, total_score in table_scores.items():
            avg_scores[table] = total_score / table_counts[table]
        
        return avg_scores
    
    def _select_top_tables(
        self, 
        table_scores: Dict[str, float], 
        top_k: int
    ) -> Set[str]:
        """Select top K tables by score"""
        sorted_tables = sorted(
            table_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        top_tables = {table for table, _ in sorted_tables[:top_k]}
        return top_tables
    
    def _build_grounded_schema(
        self,
        column_results: List[Dict[str, Any]],
        top_tables: Set[str],
        full_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build grounded schema with only relevant elements"""
        grounded_schema = {
            "tables": {},
            "relationships": []
        }
        
        # Track which columns to include for each table
        table_columns = defaultdict(set)
        
        # Add relevant columns from search results
        for result in column_results:
            table_name = result['metadata']['table']
            if table_name in top_tables:
                column_name = result['metadata']['column']
                table_columns[table_name].add(column_name)
        
        # Build table schemas
        for table_name in top_tables:
            if table_name not in full_schema['tables']:
                continue
            
            full_table = full_schema['tables'][table_name]
            
            # Always include primary keys and foreign keys
            pk_columns = set(full_table.get('primary_keys', []))
            fk_columns = {fk['column'] for fk in full_table.get('foreign_keys', [])}
            
            # Combine with retrieved columns
            selected_columns = table_columns[table_name] | pk_columns | fk_columns
            
            # Filter columns
            filtered_columns = [
                col for col in full_table['columns']
                if col['name'] in selected_columns
            ]
            
            # Add to grounded schema
            grounded_schema['tables'][table_name] = {
                "name": table_name,
                "columns": filtered_columns,
                "primary_keys": full_table.get('primary_keys', []),
                "foreign_keys": full_table.get('foreign_keys', []),
                "description": full_table.get('description', '')
            }
        
        # Add relevant relationships
        for rel in full_schema.get('relationships', []):
            if rel['from_table'] in top_tables and rel['to_table'] in top_tables:
                grounded_schema['relationships'].append(rel)
        
        return grounded_schema
    
    def get_schema_summary(self, schema: Dict[str, Any]) -> str:
        """Generate a text summary of the schema for LLM context"""
        summary_parts = []
        
        summary_parts.append("Database Schema:")
        summary_parts.append("=" * 50)
        
        for table_name, table_info in schema['tables'].items():
            summary_parts.append(f"\nTable: {table_name}")
            summary_parts.append(f"Description: {table_info.get('description', '')}")
            
            if table_info.get('primary_keys'):
                summary_parts.append(f"Primary Keys: {', '.join(table_info['primary_keys'])}")
            
            summary_parts.append("Columns:")
            for col in table_info['columns']:
                col_desc = f"  - {col['name']} ({col['type']})"
                if not col['nullable']:
                    col_desc += " NOT NULL"
                if col.get('description'):
                    col_desc += f" - {col['description']}"
                summary_parts.append(col_desc)
            
            if table_info.get('foreign_keys'):
                summary_parts.append("Foreign Keys:")
                for fk in table_info['foreign_keys']:
                    summary_parts.append(
                        f"  - {fk['column']} -> {fk['references_table']}.{fk['references_column']}"
                    )
        
        if schema.get('relationships'):
            summary_parts.append("\nRelationships:")
            for rel in schema['relationships']:
                summary_parts.append(
                    f"  {rel['from_table']}.{rel['from_column']} -> {rel['to_table']}.{rel['to_column']}"
                )
        
        return '\n'.join(summary_parts)
