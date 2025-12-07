"""
Pipeline Orchestrator - Manages the NL2SQL Flow
"""
import json
from typing import Dict, Any, Optional
from backend.core.pseudo_sql_generator import PseudoSQLGenerator
from backend.core.schema_introspector import SchemaIntrospector
from backend.core.embedding_manager import get_embedding_manager
from backend.core.sql_generator import SQLGenerator
from backend.core.sql_debugger import SQLDebugger
from backend.core.sql_judge import SQLJudge
from backend.utils.llm_client import get_llm_client

class PipelineOrchestrator:
    def __init__(self):
        self.pseudo_sql_generator = PseudoSQLGenerator()
        self.schema_introspector = SchemaIntrospector()
        self.embedding_manager = get_embedding_manager()
        self.sql_generator = SQLGenerator()
        self.sql_debugger = SQLDebugger()
        self.sql_judge = SQLJudge()
        self.llm_client = get_llm_client()
        
        self.max_debug_retries = 3
        self.confidence_threshold = 0.7
        self._full_schema = None

    def clear_embeddings(self):
        """Clear existing embeddings from Qdrant"""
        print("Clearing existing Qdrant collections...")
        try:
             # This depends on embedding_manager having a method or exposing client
             # We'll rely on recreating the collection in create_index usually,
             # but to be sure we explicitly delete if possible.
             if self.embedding_manager.client:
                 self.embedding_manager.client.delete_collection(self.embedding_manager.collection_name)
                 print("✓ Cleared 'schema_embeddings' collection")
        except Exception as e:
             print(f"Warning clearing embeddings: {e}")

    def initialize_embeddings(self, force_refresh: bool = False):
        print("Initializing schema embeddings...")
        schema = self.schema_introspector.introspect()
        if not schema or not schema.get("tables"):
            print("No tables found.")
            return
            
        embeddings, metadata = self.embedding_manager.embed_schema(schema)
        if len(embeddings) > 0:
            self.embedding_manager.create_index(embeddings, metadata)
            print("Embeddings initialized successfully.")
        else:
            print("Failed to generate embeddings (Check API Key?)")

    def process_query(self, question: str, max_retries: int = 3, confidence_threshold: float = 0.7, mode: str = "admin", store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Process User Query
        Mode: 'admin' (full access) or 'client' (restricted)
        """
        print(f"\n🔵 Processing Query ({mode}): {question}")
        
        try:
            # 0. Fast Greeting Check (Heuristic)
            greeting_response = self._check_greeting(question)
            if greeting_response:
                print("⚡ Fast Path: Greeting detected.")
                return {
                    "question": question,
                    "answer": greeting_response,
                    "products": [],
                    "sql": None
                }
            
            # 1. Pseudo SQL
            pseudo_result = self.pseudo_sql_generator.generate(question)
            
            # 1b. Check for Chitchat/Greeting (NO_SQL)
            if pseudo_result.get("pseudo_sql") == "NO_SQL":
                print("💬 Detected General Conversation")
                return {
                    "question": question,
                    "answer": pseudo_result.get("message", "Hello! How can I help you?"),
                    "products": [],
                    "sql": None
                }
            
            # 2. Get Schema (Full or Search)
            if not self._full_schema:
                self._full_schema = self.schema_introspector.introspect()
                
            # FAST PATH: If schema is small, skip vector search to reduce latency
            table_count = len(self._full_schema.get('tables', {}))
            if table_count < 20:
                print(f"⚡ Fast Path: Schema is small ({table_count} tables). Skipping vector search.")
                grounded_schema = {"tables": self._full_schema['tables']}
            else:
                # Try vector search for relevant columns
                try:
                    results = self.embedding_manager.search(question, top_k=5)
                    grounded_schema = {"tables": self._full_schema['tables']} 
                    # Note: In a real large-scale system, we would filter here.
                except Exception as e:
                    print(f"Vector search failed (using full schema): {e}")
                    grounded_schema = {"tables": self._full_schema['tables']}

            # 3. Generate SQL with Secure System Prompt
            
            # Construct the secure prompt context
            secure_prompt_context = """
            You are a secure NL2SQL engine for a commerce platform.
            You generate SQL ONLY using the database schema below.
            You MUST obey all access-control rules.
            Never reveal restricted or sensitive information.
            
            ===========================
            ACCESS CONTROL RULES
            ===========================
            
            USER PERMISSIONS:
            1. Product browsing (id, title, price, category, description, image_url, availability > 0) - Always select 'id' for linking.
            2. Own order history (products bought, quantity, time).
            3. Category listing.
            Users CANNOT see: exact stock, revenue/stats, other users, admin tables.
            
            USER SQL RULES:
            - Output plain SQL only.
            - Filter personal queries using: user_id = {CURRENT_USER_ID} (Assume ID=1 for now if not provided).
            - For product browsing, never select 'stock' column directly, only use in WHERE clause (stock > 0).
            
            ADMIN PERMISSIONS:
            - Full access: All users, products, stock, revenue, analytics.
            """
            
            mode_instruction = ""
            if mode == "client":
                mode_instruction = (
                    "Role: USER. STRICTLY enforce user permissions.\n"
                    "Do NOT allow access to 'users', 'admins', 'stores', 'revenue', 'stock'.\n"
                    "If the user asks for these, generate SQL: SELECT 'Access Denied' as message;\n"
                    "Only allow filtering 'products' by visible columns."
                )
            else:
                if store_id:
                    mode_instruction = (
                        f"Role: STORE ADMIN (ID: {store_id}).\n"
                        f"You MUST restrict all data to Store ID {store_id}.\n"
                        f" - For 'products', 'bookings', 'fact_sales', append: WHERE store_id = {store_id}\n"
                        f" - For 'orders', DO NOT use 'orders' table directly (it has no store_id). Use 'fact_sales' instead to calculate revenue/counts.\n"
                        f" - If joining tables, ensure the store isolation is preserved.\n"
                        f" - Example: SELECT SUM(total_amount) FROM fact_sales WHERE store_id = {store_id}"
                    )
                else:
                    mode_instruction = "Role: SUPER ADMIN. Full access granted. Return JSON format with 'description' and 'sql'."

            sql_result = self.sql_generator.generate(
                question=f"{secure_prompt_context}\n{mode_instruction}\nQuestion: {question}",
                pseudo_sql=pseudo_result.get('pseudo_sql', ''),
                grounded_schema=grounded_schema
            )
            
            # 3b. Security Validation (Hard Check)
            # 3b. Security Validation (Hard Check)
            if mode == "client":
                if not self._validate_client_sql(sql_result.get('sql', '')):
                    return {
                        "question": question,
                        "answer": "I cannot access that information.",
                        "products": [],
                        "sql": None
                    }

            sql = sql_result.get('sql', sql_result) if isinstance(sql_result, dict) else sql_result
            if isinstance(sql, str):
                sql = sql.strip().rstrip(';')
            
            # 4. Debug/Execute
            debug_res = self.sql_debugger.execute_and_debug(
                sql=sql,
                original_question=question,
                schema_context=str(grounded_schema),
                max_retries=max_retries
            )
            
            if not debug_res['success']:
                return {
                    "question": question,
                    "answer": f"I couldn't process that query. Error: {debug_res.get('error')}",
                    "products": [],
                    "sql": None
                }
                
            results = debug_res['results']
            final_sql = debug_res['sql']
            
            # 5. Summarize
            summary = self._generate_summary(question, results, mode)
            
            return {
                "question": question,
                "answer": summary,
                "products": results if mode == "client" else None,
                "sql": final_sql if mode == "admin" else None
            }
            
        except Exception as e:
            print(f"Orchestrator Error: {e}")
    def _check_greeting(self, question: str) -> Optional[str]:
        """Check for common greetings to return fast response"""
        q = question.strip().lower()
        greetings = {
            "hi": "Hello! I am VyaparAI, your shopping assistant. How can I help you regarding products?",
            "hello": "Hello! Looking for something specific today?",
            "hey": "Hey there! How can I help you?",
            "good morning": "Good morning! Ready to shop?",
            "good afternoon": "Good afternoon!",
            "good evening": "Good evening!",
            "thanks": "You're welcome! Let me know if you need anything else.",
            "thank you": "Happy to help!",
            "help": "I can help you find products, check prices, or track your orders. Just ask!",
            "who are you": "I am VyaparAI, an AI-powered assistant designed to help you shop."
        }
        
        # Exact match or starts with greeting
        if q in greetings:
            return greetings[q]
            
        for g, response in greetings.items():
            if q.startswith(g + " ") or q.startswith(g + ","):
                return response
                
        return None

    def _validate_client_sql(self, sql: str) -> bool:
        """
        Check if selfective logic blocks forbidden tables.
        """
        import re
        sql_lower = sql.lower()
        forbidden_tables = ['users', 'admins', 'stores', 'fact_sales', 'revenue', 'admin_password_reset_tokens']
        
        for table in forbidden_tables:
            pattern = r'\b(from|join)\s+(?:["\[\]]?\w+["\[\]]?\.)?["\[\]]?' + table + r'["\[\]]?\b'
            if re.search(pattern, sql_lower):
                print(f"⚠️ Security Block: Attempted access to {table}")
                return False
        return True

    def _generate_summary(self, question, results, mode):
        if not results: return "No results found."
        
        preview = str(results[:5])
        
        prompt = f"""
        Question: {question}
        Data: {preview}
        
        You are {mode == 'client' and 'a friendly shopping assistant' or 'a data analyst'}.
        Summarize these results in 1-2 sentences. {mode == 'client' and 'Be enthusiastic.' or 'Be factual.'}
        """
        try:
            return self.llm_client.generate(prompt)
        except:
            return f"Found {len(results)} results."

_orchestrator = None
def get_pipeline_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = PipelineOrchestrator()
    return _orchestrator
