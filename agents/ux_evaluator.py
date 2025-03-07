from crewai import Agent
from typing import Any


def create_ux_evaluator(llm: Any = None) -> Agent:
    """
    Creates a UX Evaluator agent that specializes in identifying user experience issues.
    
    Args:
        llm: Language model to use for the agent
        
    Returns:
        Agent: CrewAI Agent configured for UX evaluation
    """

    
    return Agent(
        role='User Experience Evaluator',
        goal='Examine the web page content and provide feedback on usability and design aspects, '
             'including navigation, layout clarity, and visual accessibility. Identify potential areas for improvement.',
        backstory='You are a seasoned UX expert who reviews websites for usability issues. '
                 'Your recommendations should be actionable and improve the overall user experience.',
        verbose=True,
        llm=llm,
        max_iters=1
    )