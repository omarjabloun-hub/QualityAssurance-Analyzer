from crewai import Task
from typing import Any

def create_analyze_accessibility_task(agent: Any, html_content: str, url: str) -> Task:
    """
    Creates a task for analyzing accessibility issues in a web page.
    
    Args:
        agent: The agent to assign this task to
        html_content: HTML content of the web page
        url: URL of the web page
        
    Returns:
        Task: CrewAI Task for accessibility analysis
    """
    expected_output_schema = [
        {
            "id": "a1",
            "type": "accessibility",
            "severity": "critical",
            "message": "Image lacks alt text for screen readers",
            "element": "<img src='logo.png'>",
            "line": 23
        }
    ]
    return Task(
        description=f"""
        Analyze the HTML content from {url} for accessibility issues based on WCAG guidelines.
        
        HTML Content:
        ```html
        {html_content[:5000]}... (truncated for brevity)
        ```
        
        For each issue identified, provide:
        - A unique ID with prefix 'a' (e.g., 'a1', 'a2')
        - Type: 'accessibility'
        - Severity: one of ['info', 'warning', 'critical']
        - A clear message describing the issue
        - The affected HTML element (if applicable)
        - Approximate line number (if possible to determine)
        
        Your output should be a valid JSON list of issues in the following format:
        [
            {{
                "id": "a1",
                "type": "accessibility",
                "severity": "critical",
                "message": "Image lacks alt text for screen readers",
                "element": "<img src='logo.png'>",
                "line": 23
            }},
            ...
        ]
        """,
        agent=agent,
        expected_output="A JSON-formatted list of accessibility issues, each containing 'id', 'type', 'severity', 'message', 'element', and 'line' fields."
    )