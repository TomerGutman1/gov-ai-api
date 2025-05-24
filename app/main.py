"""
Government AI API - Main FastAPI Application
This service provides AI-powered analysis of Israeli government decisions using PandasAI and OpenAI.
"""

import os
from typing import Dict, Any
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# ---- Initialize Supabase Client ----
def get_supabase_client() -> Client:
    """Initialize and return Supabase client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        raise ValueError("Missing Supabase credentials in environment variables")
    
    return create_client(url, key)

# ---- Load Data from Supabase ----
def load_dataframe() -> pd.DataFrame:
    """Load Israeli government decisions from Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Load ALL records using pagination
        all_data = []
        page_size = 1000
        offset = 0
        
        while True:
            response = supabase.table("israeli_government_decisions").select("*").range(offset, offset + page_size - 1).execute()
            
            if not response.data:
                break
                
            all_data.extend(response.data)
            
            # If we got less than page_size records, we've reached the end
            if len(response.data) < page_size:
                break
                
            offset += page_size
            logger.info(f"Loaded {len(all_data)} records so far...")
        
        if not all_data:
            logger.warning("No data found in israeli_government_decisions table")
            return pd.DataFrame()
        
        df = pd.DataFrame(all_data)
        logger.info(f"Loaded total of {len(df)} records from Supabase")
        return df
    
    except Exception as e:
        logger.error(f"Error loading data from Supabase: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ---- Initialize PandasAI ----
def initialize_pandasai(df: pd.DataFrame) -> SmartDataframe:
    """Initialize PandasAI with OpenAI LLM"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OpenAI API key in environment variables")
    
    llm = OpenAI(api_token=api_key, model="gpt-4o")
    
    # Configure PandasAI for better Hebrew support and conversational answers
    config = {
        "llm": llm,
        "conversational": True,
        "enable_cache": True,
        "max_retries": 2,
        "verbose": True,
        "enforce_privacy": True,
        "custom_prompts": {
            "generate_python_code": """
            You are analyzing Israeli government decisions data.
            The data may contain Hebrew text, so handle encoding properly.
            Generate Python code to answer: {question}
            
            Available columns: {columns}
            
            Total records in dataset: {total_records}
            
            Instructions:
            1. Use proper pandas syntax
            2. Handle Hebrew text encoding if needed
            3. Return clear, informative results
            4. Be aware this is a large dataset with over 24,000 records
            """.replace("{total_records}", str(len(df)))
        }
    }
    
    return SmartDataframe(df, config=config)

# ---- Request/Response Models ----
class QuestionRequest(BaseModel):
    question: str
    
class AnswerResponse(BaseModel):
    answer: str
    success: bool
    error: str = None

# ---- Initialize FastAPI App ----
app = FastAPI(
    title="Government AI API",
    description="AI-powered analysis of Israeli government decisions",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:*",
        "https://lovable.dev",
        "https://*.lovable.dev",
        os.getenv("ALLOWED_ORIGIN", "*")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data on startup
df = None
sdf = None

@app.on_event("startup")
async def startup_event():
    """Load data and initialize PandasAI on startup"""
    global df, sdf
    try:
        df = load_dataframe()
        if not df.empty:
            sdf = initialize_pandasai(df)
            logger.info("Successfully initialized PandasAI")
        else:
            logger.warning("Starting with empty dataframe")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")

# ---- API Endpoints ----
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Government AI API",
        "data_loaded": df is not None and not df.empty
    }

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about Israeli government decisions
    
    The AI will analyze the data and provide insights based on your question.
    Questions can be in Hebrew or English.
    """
    try:
        if sdf is None:
            raise HTTPException(
                status_code=503,
                detail="Service not ready. Data not loaded."
            )
        
        # Log the question
        logger.info(f"Processing question: {request.question}")
        
        # Get answer from PandasAI
        answer = sdf.chat(request.question)
        
        # Convert answer to string if it's not already
        answer_str = str(answer) if answer is not None else "לא נמצאה תשובה"
        
        logger.info(f"Generated answer: {answer_str[:100]}...")
        
        return AnswerResponse(
            answer=answer_str,
            success=True
        )
    
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return AnswerResponse(
            answer="",
            success=False,
            error=str(e)
        )

@app.get("/stats")
async def get_stats():
    """Get statistics about the loaded data"""
    if df is None or df.empty:
        return {
            "total_records": 0,
            "columns": [],
            "data_loaded": False
        }
    
    return {
        "total_records": len(df),
        "columns": df.columns.tolist(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "data_loaded": True,
        "sample_record": df.iloc[0].to_dict() if len(df) > 0 else None
    }

@app.post("/reload")
async def reload_data():
    """Reload data from Supabase"""
    global df, sdf
    try:
        df = load_dataframe()
        if not df.empty:
            sdf = initialize_pandasai(df)
            return {
                "success": True,
                "message": f"Reloaded {len(df)} records",
                "records_count": len(df)
            }
        else:
            return {
                "success": False,
                "message": "No data found in database",
                "records_count": 0
            }
    except Exception as e:
        logger.error(f"Reload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "api": "healthy",
        "database": "unknown",
        "ai_service": "unknown",
        "data_loaded": False
    }
    
    # Check database connection
    try:
        supabase = get_supabase_client()
        # Simple query to test connection
        supabase.table("israeli_government_decisions").select("id").limit(1).execute()
        health_status["database"] = "healthy"
    except:
        health_status["database"] = "unhealthy"
    
    # Check AI service
    if sdf is not None:
        health_status["ai_service"] = "healthy"
        health_status["data_loaded"] = True
    
    # Overall status
    all_healthy = all(v == "healthy" for v in health_status.values() if isinstance(v, str))
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "details": health_status
    }

@app.get("/count")
async def get_count():
    """Get total count of records in database"""
    try:
        supabase = get_supabase_client()
        # Use count parameter to get total count efficiently
        response = supabase.table("israeli_government_decisions").select("*", count='exact').execute()
        
        return {
            "total_records": response.count,
            "loaded_records": len(df) if df is not None else 0,
            "status": "all_loaded" if df is not None and len(df) == response.count else "partial"
        }
    except Exception as e:
        logger.error(f"Count error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)