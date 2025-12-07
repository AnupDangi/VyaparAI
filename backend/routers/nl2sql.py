"""
NL2SQL Router - Handles Natural Language Queries
Supports separate Client and Admin modes.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from backend.core.pipeline_orchestrator import get_pipeline_orchestrator

router = APIRouter()

class NLQueryRequest(BaseModel):
    question: str
    max_retries: Optional[int] = 3
    confidence_threshold: Optional[float] = 0.7
    store_id: Optional[int] = None

@router.post("/client/query")
def client_query(request: NLQueryRequest):
    """
    Client-facing endpoint:
    - Restricted to safe queries (products, orders, status)
    - Formatted output for consumers (friendly tone)
    """
    try:
        orchestrator = get_pipeline_orchestrator()
        result = orchestrator.process_query(
            question=request.question,
            max_retries=request.max_retries,
            confidence_threshold=request.confidence_threshold,
            mode="client"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/query")
def admin_query(request: NLQueryRequest):
    """
    Admin-facing endpoint:
    - Full SQL access (analytics, sales, users, forecasting)
    - Returns SQL, results, and analytical summary
    """
    try:
        # In a real app, verify admin token here
        orchestrator = get_pipeline_orchestrator()
        result = orchestrator.process_query(
            question=request.question,
            max_retries=request.max_retries,
            confidence_threshold=request.confidence_threshold,
            mode="admin",
            store_id=request.store_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
