"""
Base Node Class
"""

from abc import ABC, abstractmethod
from core.state import GraphState


class BaseNode(ABC):
    """Abstract base class for all nodes"""
    
    @abstractmethod
    def execute(self, state: GraphState) -> GraphState:
        """
        Execute the node's logic
        
        Args:
            state: Current graph state
        
        Returns:
            Updated graph state
        """
        pass
    
    def log(self, message: str):
        """Print log message"""
        print(f"  {message}")
