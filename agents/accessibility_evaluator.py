from crewai import Agent
from typing import Any

def create_accessibility_evaluator(llm: Any = None) -> Agent:
    """
    Creates an Accessibility Evaluator agent that specializes in identifying accessibility issues.
    
    Args:
        llm: Language model to use for the agent
        
    Returns:
        Agent: CrewAI Agent configured for accessibility evaluation
    """
    return Agent(
        role='Accessibility Expert',
        goal='Analyze web pages for accessibility compliance and identify barriers for users with disabilities. '
             'Evaluate against WCAG standards and provide specific recommendations for improvements.',
        backstory='You are an accessibility consultant with expertise in WCAG guidelines and assistive technologies. '
                 'You help organizations make their digital content accessible to all users, including those with disabilities.',
        verbose=True,
        llm=llm,
        max_iters=1
    )