from crewai import Agent
from typing import Any

def create_performance_evaluator(llm: Any = None) -> Agent:
    """
    Creates a Performance Evaluator agent that specializes in identifying performance issues.
    
    Args:
        llm: Language model to use for the agent
        
    Returns:
        Agent: CrewAI Agent configured for performance evaluation
    """
    return Agent(
        role='Performance Optimization Expert',
        goal='Analyze web page content for potential performance bottlenecks, including large assets, '
             'inefficient code patterns, and loading optimizations.',
        backstory='You are a web performance engineer who has helped numerous companies optimize their '
                 'websites for speed and efficiency. You can identify performance issues by examining '
                 'HTML structure, resource loading, and code patterns.',
        verbose=True,
        llm=llm,
        max_iters=1
    )