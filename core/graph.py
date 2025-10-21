"""
Node Types and Edge Conditions
"""

from enum import Enum
from core.state import GraphState
from config import AgentConfig


class NodeType(Enum):
    """Types of nodes in the agent graph"""
    START = "start"
    ANALYZE_TARGET = "analyze_target"
    GENERATE_VIDEO = "generate_video"
    TAKE_SCREENSHOT = "take_screenshot"
    ANALYZE_CURRENT = "analyze_current"
    COMPARE = "compare"
    ADJUST_PARAMETERS = "adjust_parameters"
    STOP_SUCCESS = "stop_success"
    STOP_MAX_ITERATIONS = "stop_max_iterations"


class EdgeConditions:
    """Edge conditions that determine graph transitions"""
    
    @staticmethod
    def should_stop_success(state: GraphState, config: AgentConfig) -> bool:
        """Check if success threshold reached"""
        if state.comparison_result is None:
            return False
        return state.comparison_result['overall_score'] >= config.success_threshold
    
    @staticmethod
    def should_stop_max_iterations(state: GraphState, config: AgentConfig) -> bool:
        """Check if max iterations reached"""
        return state.iteration >= config.max_iterations
    
    @staticmethod
    def should_continue(state: GraphState, config: AgentConfig) -> bool:
        """Check if should continue iterating"""
        return not (EdgeConditions.should_stop_success(state, config) or 
                   EdgeConditions.should_stop_max_iterations(state, config))
