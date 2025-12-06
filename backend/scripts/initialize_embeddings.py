"""
Initialize Embeddings Script
Run this script once to generate embeddings for your database schema
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.core.pipeline_orchestrator import PipelineOrchestrator


def main():
    """Initialize embeddings for the database"""
    print("=" * 60)
    print("Natural Language to SQL - Embedding Initialization")
    print("=" * 60)
    print()
    
    try:
        # Create pipeline orchestrator
        pipeline = PipelineOrchestrator()
        
        # Initialize embeddings
        pipeline.initialize_embeddings(force_refresh=False)
        
        print()
        print("=" * 60)
        print("✓ Initialization Complete!")
        print("=" * 60)
        print()
        print("You can now start the API server:")
        print("  python backend/main.py")
        print()
        print("Or use uvicorn:")
        print("  uvicorn backend.main:app --reload")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ Initialization Failed!")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
