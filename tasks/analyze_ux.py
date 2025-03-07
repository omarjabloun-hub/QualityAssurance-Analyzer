from crewai import Task
from typing import Any, Dict, List

def create_analyze_ux_task(agent: Any, html_content: str, url: str) -> Task:
    """
    Creates a task for analyzing user experience issues in a web page.
    
    Args:
        agent: The agent to assign this task to
        html_content: HTML content of the web page
        url: URL of the web page
        
    Returns:
        Task: CrewAI Task for UX analysis
    """

    expected_output_schema = [
        {
            "id": "u1",
            "type": "ux",
            "severity": "warning",
            "message": "Navigation menu lacks clear visual hierarchy",
            "element": "<nav class='main-navigation'>",
            "line": 45
        }
    ]
    return Task(
        description=f"""
        Analyze the HTML content from {url} for user experience issues.
        
        HTML Content:
        ```html
        {html_content[:5000]}... (truncated for brevity)
        ```
        
        For each issue identified, provide:
        - A unique ID with prefix 'u' (e.g., 'u1', 'u2')
        - Type: 'ux'
        - Severity: one of ['info', 'warning', 'critical']
        - A clear message describing the issue
        - The affected HTML element (if applicable)
        - Approximate line number (if possible to determine)
        
        Your output should be a valid JSON list of issues in the following format:
        [
            {{
                "id": "u1",
                "type": "ux",
                "severity": "warning",
                "message": "Navigation menu lacks clear visual hierarchy",
                "element": "<nav class='main-navigation'>",
                "line": 45
            }},
            ...
        ]
        """,
        agent=agent,
        expected_output="A JSON-formatted list of UX issues, each containing 'id', 'type', 'severity', 'message', 'element', and 'line' fields."
    )