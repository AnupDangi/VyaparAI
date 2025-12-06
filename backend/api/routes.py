"""
API Routes - Simplified to single NL-to-SQL endpoint
"""
from fastapi import APIRouter, HTTPException
from backend.api.models import NLQueryRequest
from backend.core.pipeline_orchestrator import get_pipeline_orchestrator

router = APIRouter()


@router.post("/nl-to-sql")
async def nl_to_sql(request: NLQueryRequest):
    """
    Convert natural language to SQL and execute
    
    Main endpoint - converts your question to SQL, runs it, and returns results
    """
    try:
        orchestrator = get_pipeline_orchestrator()
        result = orchestrator.process_query(
            question=request.question,
            max_retries=request.max_retries,
            confidence_threshold=request.confidence_threshold
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
