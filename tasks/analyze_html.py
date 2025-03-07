from crewai import Task
from typing import Any

def create_analyze_html_task(agent: Any, html_content: str, url: str) -> Task:
    """
    Creates a task for analyzing HTML structure issues in a web page.
    
    Args:
        agent: The agent to assign this task to
        html_content: HTML content of the web page
        url: URL of the web page
        
    Returns:
        Task: CrewAI Task for HTML analysis
    """
    expected_output_schema = [
        {
            "id": "h1",
            "type": "html",
            "severity": "warning",
            "message": "Heading tags are not in hierarchical order",
            "element": "<h3>Section title</h3>",
            "line": 78
        }
    ]
    return Task(
        description=f"""
        Analyze the HTML content from {url} for HTML structure, semantics, and best practices issues.
        
        HTML Content:
        ```html
        {html_content[:5000]}... (truncated for brevity)
        ```
        
        For each issue identified, provide:
        - A unique ID with prefix 'h' (e.g., 'h1', 'h2')
        - Type: 'html'
        - Severity: one of ['info', 'warning', 'critical']
        - A clear message describing the issue
        - The affected HTML element (if applicable)
        - Approximate line number (if possible to determine)
        
        Your output should be a valid JSON list of issues in the following format:
        [
            {{
                "id": "h1",
                "type": "html",
                "severity": "warning",
                "message": "Heading tags are not in hierarchical order",
                "element": "<h3>Section title</h3>",
                "line": 78
            }},
            ...
        ]
        """,
        agent=agent,
        expected_output="A JSON-formatted list of html issues, each containing 'id', 'type', 'severity', 'message', 'element', and 'line' fields."
    )