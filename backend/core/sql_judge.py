"""
SQL Judge - Evaluates SQL quality and confidence
"""
import os
from typing import Dict, Any, List
from backend.utils.llm_client import get_llm_client
from dotenv import load_dotenv

load_dotenv()


class SQLJudge:
    """Evaluates SQL query quality and correctness"""
    
    def __init__(self):
        self.llm = get_llm_client()
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
    
    def evaluate(
        self,
        question: str,
        sql: str,
        results: List[Dict[str, Any]],
        schema_context: str
    ) -> Dict[str, Any]:
        """
        Evaluate SQL query quality and confidence
        
        Args:
            question: Original natural language question
            sql: Generated SQL query
            results: Query execution results
            schema_context: Schema information for context
            
        Returns:
            Dictionary with confidence score, assessment, and recommendations
        """
        # Prepare results preview
        results_preview = self._format_results_preview(results)
        
        system_prompt = """You are an expert SQL quality evaluator. Assess whether a SQL query correctly answers a natural language question.

Your task:
1. Analyze if the SQL query structure matches the question intent
2. Check if the results make sense for the question
3. Identify any potential issues or improvements
4. Provide a confidence score from 0.0 to 1.0

Be critical but fair. Consider:
- Does the query answer the right question?
- Are the results relevant and formatted correctly?
- Are there any logical errors or missing filters?
- Could the query be more efficient?"""
        
        prompt = f"""Question: {question}

SQL Query:
{sql}

Schema Context:
{schema_context}

Results Preview (first 5 rows):
{results_preview}

Evaluate this SQL query and provide:
1. Confidence score (0.0 to 1.0) - how confident are you this answers the question?
2. Assessment (one line) - brief evaluation
3. Issues (if any) - what's wrong or could be improved
4. Recommendation - should this be accepted or regenerated?

Format your response as:
CONFIDENCE: <score>
ASSESSMENT: <one line assessment>
ISSUES: <issues or "None">
RECOMMENDATION: <ACCEPT or REGENERATE>"""
        
        try:
            response = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.0
            )
            
            # Parse the response
            evaluation = self._parse_evaluation(response)
            
            # Add metadata
            evaluation['passed_threshold'] = evaluation['confidence'] >= self.confidence_threshold
            evaluation['threshold'] = self.confidence_threshold
            evaluation['row_count'] = len(results)
            
            return evaluation
        
        except Exception as e:
            print(f"Error evaluating SQL: {e}")
            return {
                "confidence": 0.5,
                "assessment": "Evaluation failed",
                "issues": str(e),
                "recommendation": "UNKNOWN",
                "passed_threshold": False,
                "threshold": self.confidence_threshold,
                "error": str(e)
            }
    
    def _format_results_preview(
        self,
        results: List[Dict[str, Any]],
        max_rows: int = 5
    ) -> str:
        """Format results for LLM preview"""
        if not results:
            return "No results returned"
        
        preview_results = results[:max_rows]
        
        # Create table format
        if not preview_results:
            return "Empty result set"
        
        # Get column names
        columns = list(preview_results[0].keys())
        
        # Format as table
        lines = []
        lines.append(" | ".join(columns))
        lines.append("-" * 60)
        
        for row in preview_results:
            values = [str(row.get(col, 'NULL'))[:30] for col in columns]
            lines.append(" | ".join(values))
        
        if len(results) > max_rows:
            lines.append(f"... and {len(results) - max_rows} more rows")
        
        return '\n'.join(lines)
    
    def _parse_evaluation(self, response: str) -> Dict[str, Any]:
        """Parse LLM evaluation response"""
        evaluation = {
            "confidence": 0.5,
            "assessment": "",
            "issues": "",
            "recommendation": "UNKNOWN"
        }
        
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("CONFIDENCE:"):
                try:
                    score_str = line.replace("CONFIDENCE:", "").strip()
                    evaluation["confidence"] = float(score_str)
                except ValueError:
                    pass
            
            elif line.startswith("ASSESSMENT:"):
                evaluation["assessment"] = line.replace("ASSESSMENT:", "").strip()
            
            elif line.startswith("ISSUES:"):
                evaluation["issues"] = line.replace("ISSUES:", "").strip()
            
            elif line.startswith("RECOMMENDATION:"):
                recommendation = line.replace("RECOMMENDATION:", "").strip().upper()
                if recommendation in ["ACCEPT", "REGENERATE"]:
                    evaluation["recommendation"] = recommendation
        
        return evaluation
    
    def quick_check(
        self,
        sql: str,
        row_count: int,
        error: str = None
    ) -> Dict[str, Any]:
        """
        Quick quality check without LLM
        
        Args:
            sql: SQL query
            row_count: Number of rows returned
            error: Error message if query failed
            
        Returns:
            Basic quality assessment
        """
        if error:
            return {
                "confidence": 0.0,
                "assessment": "Query execution failed",
                "issues": error,
                "recommendation": "REGENERATE",
                "passed_threshold": False
            }
        
        # Basic heuristics
        confidence = 0.7  # Default
        issues = []
        
        # Check for potential issues
        if row_count == 0:
            confidence -= 0.2
            issues.append("No results returned")
        
        if "SELECT *" in sql.upper():
            confidence -= 0.1
            issues.append("Uses SELECT * which may be inefficient")
        
        return {
            "confidence": max(0.0, confidence),
            "assessment": "Quick check based on heuristics",
            "issues": "; ".join(issues) if issues else "None",
            "recommendation": "ACCEPT" if confidence >= 0.5 else "REGENERATE",
            "passed_threshold": confidence >= self.confidence_threshold,
            "threshold": self.confidence_threshold
        }
