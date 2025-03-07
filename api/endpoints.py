from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any
import httpx
import time
import os
import uuid
# Import Utils
from utils.clean_html import clean_html

# Import LLM
from core.llm import llm_gpt

# Import crew and agent factories
from agents.ux_evaluator import create_ux_evaluator
from agents.accessibility_evaluator import create_accessibility_evaluator
from agents.html_evaluator import create_html_evaluator
from agents.performance_evaluator import create_performance_evaluator

# Import task factories
from tasks.analyze_ux import create_analyze_ux_task
from tasks.analyze_accessibility import create_analyze_accessibility_task
from tasks.analyze_html import create_analyze_html_task
from tasks.analyze_performance import create_analyze_performance_task

# Import crew
from crew.qa_analyzer import QAAnalyzerCrew

# Pydantic models for request and response validation
class AnalyzeRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL of the web page to analyze")

class QualityIssue(BaseModel):
    id: str = Field(..., description="Unique identifier for the issue")
    type: str = Field(..., description="Category of the issue (html, ux, accessibility, etc.)")
    severity: str = Field(..., description="Severity level of the issue (info, warning, critical)")
    message: str = Field(..., description="Description of the issue")
    element: Optional[str] = Field(None, description="Affected HTML element")
    line: Optional[int] = Field(None, description="Line number where the issue occurs")

class AnalyzeResponse(BaseModel):
    url: HttpUrl
    issues: List[QualityIssue]
    analysis_time: float

# Create the router
router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_webpage(request: AnalyzeRequest):
    start_time = time.time()
    
    # Fetch HTML content
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(str(request.url))
            response.raise_for_status()
            html_content = clean_html(response.text)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, 
                            detail=f"HTTP error while fetching URL: {str(e)}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, 
                            detail=f"Request error while fetching URL: {str(e)}")
    
    # Check if content was retrieved
    if not html_content:
        raise HTTPException(status_code=422, detail="Retrieved empty content from URL")
    
    print(html_content)
    # Initialize LLM
    try:
        llm = llm_gpt
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM configuration error: {str(e)}")
    
    # Create agents
    ux_agent = create_ux_evaluator(llm)
    accessibility_agent = create_accessibility_evaluator(llm)
    html_agent = create_html_evaluator(llm)
    performance_agent = create_performance_evaluator(llm)
    
    # Create tasks
    ux_task = create_analyze_ux_task(ux_agent, html_content, str(request.url))
    accessibility_task = create_analyze_accessibility_task(accessibility_agent, html_content, str(request.url))
    html_task = create_analyze_html_task(html_agent, html_content, str(request.url))
    performance_task = create_analyze_performance_task(performance_agent, html_content, str(request.url))
    
    # Create and run crew
    crew = QAAnalyzerCrew(
        agents=[ux_agent, accessibility_agent, html_agent, performance_agent],
        tasks=[ux_task, accessibility_task, html_task, performance_task]
    )
    
    try:
        issues_data = crew.analyze()
        
        # Convert to Pydantic models
        issues = []
        for issue_data in issues_data:
            # Ensure the issue has required fields
            if not issue_data.get('id'):
                issue_data['id'] = f"auto_{uuid.uuid4().hex[:6]}"
            issues.append(QualityIssue(**issue_data))
    except Exception as e:
        raise HTTPException(status_code=500, 
                           detail=f"Error during CrewAI analysis: {str(e)}")
    
    # Calculate analysis time
    analysis_time = time.time() - start_time
    
    # Return response
    return AnalyzeResponse(
        url=request.url,
        issues=issues,
        analysis_time=analysis_time
    )

@router.get("/health")
async def health_check():
    return {"status": "healthy"}