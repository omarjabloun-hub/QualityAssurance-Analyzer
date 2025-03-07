from crewai import Crew, Process
from typing import Any, List, Dict
import json

class QAAnalyzerCrew:
    """
    A crew of agents specialized in analyzing web pages for quality issues.
    """
    
    def __init__(self, agents: List[Any], tasks: List[Any]):
        """
        Initialize the web analyzer crew.
        
        Args:
            agents: List of crewAI agents for the analysis
            tasks: List of crewAI tasks to be performed
        """
        self.agents = agents
        self.tasks = tasks
        self.crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            process=Process.sequential
        )
    
    def analyze(self) -> List[Dict]:
        """
        Run the analysis and return a combined list of issues.
        
        Returns:
            List[Dict]: Combined list of issues from all agents
        """
        # Execute the crew's tasks
        results = self.crew.kickoff()

        
        all_issues = []
        for task in self.tasks:
            result = task.output.raw
            self._process_result(result, all_issues)
            
        print(all_issues)
        return all_issues       
        
        
    
    def _process_result(self, result, all_issues):
        """
        Process a single result and add parsed issues to all_issues list.
        
        Args:
            result: The result to process
            all_issues: List to append parsed issues to
        """
        try:
            print("New Result : ")
            print(result)
            print("Old Result :")
            print(all_issues)
            # If result is already a dict or list, convert to string first
            if isinstance(result, (dict, list)):
                result_str = json.dumps(result)
            else:
                result_str = str(result)
                
            # Clean the string to ensure it's valid JSON
            # Look for JSON array pattern [...] in the result
            import re
            json_match = re.search(r'\[.*\]', result_str, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                issues = json.loads(json_str)
                
                if isinstance(issues, list):
                    all_issues.extend(issues)
                else:
                    all_issues.append(issues)
            else:
                # Try parsing the entire string as JSON
                try:
                    issues = json.loads(result_str)
                    if isinstance(issues, list):
                        all_issues.extend(issues)
                    else:
                        all_issues.append(issues)
                except json.JSONDecodeError:
                    # Create an error issue for non-JSON output
                    error_issue = {
                        "id": f"error_{len(all_issues) + 1}",
                        "type": "system",
                        "severity": "info",
                        "message": f"Failed to parse agent output: {result_str[:100]}...",
                        "element": None,
                        "line": None
                    }
                    all_issues.append(error_issue)
        except Exception as e:
            # Handle any other errors
            error_issue = {
                "id": f"error_{len(all_issues) + 1}",
                "type": "system",
                "severity": "info",
                "message": f"Error processing result: {str(e)}",
                "element": None,
                "line": None
            }
            all_issues.append(error_issue)