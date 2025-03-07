from crewai import Agent
from typing import Any

def create_html_evaluator(llm: Any = None) -> Agent:
    """
    Creates an HTML Evaluator agent that specializes in identifying HTML structure and semantic issues.
    
    Args:
        llm: Language model to use for the agent
        
    Returns:
        Agent: CrewAI Agent configured for HTML evaluation
    """
    
    return Agent(
        role='HTML Structure Analyst',
        goal='Examine HTML code for structural issues, semantic correctness, and best practices. '
             'Identify potential optimizations for better maintainability and browser compatibility.',
        backstory='You are an experienced front-end developer who specializes in HTML semantics and structure. '
                 'You have a keen eye for proper document structure and can identify issues that might affect '
                 'SEO, accessibility, or future maintainability.',
        verbose=True,
        llm=llm,
        max_iters=1
    )