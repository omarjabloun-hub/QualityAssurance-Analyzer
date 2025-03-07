from crewai import Task
from typing import Any

def create_analyze_performance_task(agent: Any, html_content: str, url: str) -> Task:
    """
    Creates a task for analyzing performance issues in a web page.
    
    Args:
        agent: The agent to assign this task to
        html_content: HTML content of the web page
        url: URL of the web page
        
    Returns:
        Task: CrewAI Task for performance analysis
    """
    expected_output_schema = [
        {
            "id": "p1",
            "type": "performance",
            "severity": "warning",
            "message": "Large unoptimized image could slow page loading",
            "element": "<img src='large-hero.jpg' width='1920' height='1080'>",
            "line": 34
        }
    ]

    return Task(
        description=f"""
        Analyze the HTML content from {url} for performance optimization opportunities.
        
        HTML Content:
        ```html
        {html_content[:5000]}... (truncated for brevity)
        ```
        
        For each issue identified, provide:
        - A unique ID with prefix 'p' (e.g., 'p1', 'p2')
        - Type: 'performance'
        - Severity: one of ['info', 'warning', 'critical']
        - A clear message describing the issue
        - The affected HTML element (if applicable)
        - Approximate line number (if possible to determine)
        
        Your output should be a valid JSON list of issues in the following format:
        [
            {{
                "id": "p1",
                "type": "performance",
                "severity": "warning",
                "message": "Large unoptimized image could slow page loading",
                "element": "<img src='large-hero.jpg' width='1920' height='1080'>",
                "line": 34
            }},
            ...
        ]
        """,
        agent=agent,
        expected_output="A JSON-formatted list of performance issues, each containing 'id', 'type', 'severity', 'message', 'element', and 'line' fields."
    )