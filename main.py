from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Optional, Dict, Any
import httpx
import uuid
import re
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from pydantic import RootModel

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Web QA Analyzer API",
    description="Analyzes web pages for quality issues using LLMs",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    @validator('severity')
    def validate_severity(cls, v):
        allowed_values = ["info", "warning", "critical"]
        if v not in allowed_values:
            raise ValueError(f"Severity must be one of {allowed_values}")
        return v

# New wrapper model to enclose a list of QualityIssue objects.
class IssuesList(RootModel[List[QualityIssue]]):
    pass

class AnalyzeResponse(BaseModel):
    url: HttpUrl
    issues: List[QualityIssue]
    analysis_time: float

# Helper to estimate line numbers in HTML content
def estimate_line_number(html_content: str, element_snippet: str) -> Optional[int]:
    if not element_snippet or not html_content:
        return None
    
    lines = html_content.split('\n')
    # Clean up the element snippet to improve matching
    clean_snippet = re.sub(r'\s+', ' ', element_snippet).strip()
    
    for i, line in enumerate(lines):
        if clean_snippet in re.sub(r'\s+', ' ', line).strip():
            return i + 1
    
    # If exact match not found, try a more flexible approach
    for i, line in enumerate(lines):
        # Extract tag name from snippet for partial matching
        tag_match = re.match(r'<(\w+)', clean_snippet)
        if tag_match and f"<{tag_match.group(1)}" in line:
            return i + 1
    
    return None

# Setup LangChain components
def setup_langchain():
    # Ensure API key is set in environment variables
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY environment variable must be set")
    
    # Create output parser using the IssuesList wrapper
    parser = PydanticOutputParser(pydantic_object=IssuesList)
    
    # Create prompt template
    template = """
    You are a web quality assurance expert. Analyze the HTML content below and identify quality issues.
    Focus on HTML structure, accessibility, user experience, and performance problems.
    
    For each issue found, provide:
    1. A unique ID (format: letter + number, e.g., 'h1', 'a2', 'u3')
    2. Type (one of: 'html', 'accessibility', 'ux', 'performance')
    3. Severity ('info', 'warning', or 'critical')
    4. A clear message describing the issue
    5. The affected HTML element (if applicable)
    6. Approximate line number (if possible to determine)
    
    HTML Content to analyze:
    {html_content}
    
    {format_instructions}
    
    Return ONLY the JSON list of issues with no additional text.
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["html_content"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Initialize LLM
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.1)    
    # Create chain
    chain = LLMChain(llm=llm, prompt=prompt)
    
    return chain, parser

# Create LangChain components
try:
    analysis_chain, output_parser = setup_langchain()
except Exception as e:
    print(f"Error setting up LangChain: {str(e)}")
    # We'll handle this during request processing

# Routes
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_webpage(request: AnalyzeRequest):
    import time
    start_time = time.time()
    
    # Check if LangChain is properly set up
    if 'analysis_chain' not in globals() or 'output_parser' not in globals():
        try:
            globals()['analysis_chain'], globals()['output_parser'] = setup_langchain()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM configuration error: {str(e)}")
    
    # Fetch HTML content
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(str(request.url))
            response.raise_for_status()
            html_content = response.text
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, 
                            detail=f"HTTP error while fetching URL: {str(e)}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, 
                            detail=f"Request error while fetching URL: {str(e)}")
    
    # Check if content was retrieved
    if not html_content:
        raise HTTPException(status_code=422, detail="Retrieved empty content from URL")
    
    # Run LLM analysis
    try:
        raw_llm_output = analysis_chain.run(html_content=html_content)
        
        # Parse the output using the wrapper model
        try:
            issues_wrapper = output_parser.parse(raw_llm_output)
            issues = issues_wrapper.__root__
        except Exception as e:
            # If structured parsing fails, try to extract issues manually
            import json
            import re
            
            json_match = re.search(r'\[.*\]', raw_llm_output, re.DOTALL)
            if json_match:
                try:
                    issues_data = json.loads(json_match.group(0))
                    issues = []
                    for issue_data in issues_data:
                        if not issue_data.get('id'):
                            issue_data['id'] = f"auto_{uuid.uuid4().hex[:6]}"
                        issues.append(QualityIssue(**issue_data))
                except:
                    issues = [
                        QualityIssue(
                            id=f"parser_{uuid.uuid4().hex[:6]}",
                            type="system",
                            severity="info",
                            message="Could not parse LLM output into the expected format. Raw analysis is available.",
                            element=None,
                            line=None
                        )
                    ]
            else:
                issues = [
                    QualityIssue(
                        id=f"parser_{uuid.uuid4().hex[:6]}",
                        type="system",
                        severity="info",
                        message=f"Could not parse LLM output: {str(e)}",
                        element=None,
                        line=None
                    )
                ]
    except Exception as e:
        raise HTTPException(status_code=500, 
                            detail=f"Error during LLM analysis: {str(e)}")
    
    # Post-process issues to estimate line numbers if not provided
    for issue in issues:
        if issue.element and not issue.line:
            issue.line = estimate_line_number(html_content, issue.element)
    
    # Calculate analysis time
    analysis_time = time.time() - start_time
    
    # Return response
    return AnalyzeResponse(
        url=request.url,
        issues=issues,
        analysis_time=analysis_time
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": app.version}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
