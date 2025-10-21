"""
Compare Node - Compare current with target metrics
"""

from nodes.base_node import BaseNode
from core.state import GraphState
from config import AgentConfig


class CompareNode(BaseNode):
    """Compare current iteration with target metrics"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
    
    def execute(self, state: GraphState) -> GraphState:
        """Compare and score current vs target"""
        print(f"\n{'='*60}")
        print(f"📊 NODE: Compare with Target")
        print(f"{'='*60}")
        
        if not state.target_metrics or not state.current_metrics or not state.current_metrics['text_detected']:
            state.comparison_result = self._empty_comparison()
            return state
        
        # Calculate individual scores
        clarity_score = self._calculate_clarity_score(state)
        position_score = self._calculate_position_score(state)
        size_score = self._calculate_size_score(state)
        
        # Calculate overall weighted score
        w = self.config.comparison_weights
        overall_score = (
            clarity_score * w['clarity'] + 
            position_score * w['position'] + 
            size_score * w['size']
        )
        
        # Store comparison result
        state.comparison_result = {
            'clarity_score': clarity_score,
            'position_score': position_score,
            'size_score': size_score,
            'overall_score': overall_score,
            'details': self._get_details(state)
        }
        
        # Print scores
        self.log(f"✅ Clarity Score: {clarity_score:.1f}/100")
        self.log(f"✅ Position Score: {position_score:.1f}/100")
        self.log(f"✅ Size Score: {size_score:.1f}/100")
        self.log(f"🎯 Overall Score: {overall_score:.1f}/100")
        
        # Store iteration result
        self._store_iteration(state)
        
        # Update best result if improved
        if state.best_result is None or \
           overall_score > state.best_result['comparison']['overall_score']:
            state.best_result = state.all_iterations[-1]
            self.log("⭐ NEW BEST!")
        
        return state
    
    def _calculate_clarity_score(self, state: GraphState) -> float:
        """Calculate clarity score based on OCR confidence"""
        if not state.target_metrics or not state.current_metrics:
            return 0
        target_conf = state.target_metrics['avg_confidence']
        current_conf = state.current_metrics['avg_confidence']
        clarity_diff = abs(target_conf - current_conf)
    def _calculate_position_score(self, state: GraphState) -> float:
        """Calculate position score based on vertical placement"""
        if not state.target_metrics or not state.current_metrics:
            return 0
        target_pos = state.target_metrics['avg_y_position']
        current_pos = state.current_metrics['avg_y_position']
        position_diff = abs(target_pos - current_pos)
    def _calculate_size_score(self, state: GraphState) -> float:
        """Calculate size score based on font size"""
        if not state.target_metrics or not state.current_metrics:
            return 0
        target_size = state.target_metrics['estimated_font_size']
        current_size = state.current_metrics.get('estimated_font_size', 0)
        
        if current_size > 0:
            size_diff = abs(target_size - current_size) / target_size
            return max(0, 100 - (size_diff * 100))
        return 0
        if current_size > 0:
            size_diff = abs(target_size - current_size) / target_size
            return max(0, 100 - (size_diff * 100))
        return 0
    
    def _get_details(self, state: GraphState) -> dict:
        """Get detailed comparison information"""
        if not state.target_metrics or not state.current_metrics:
            return {}
        
        return {
            'target_conf': state.target_metrics['avg_confidence'],
            'current_conf': state.current_metrics['avg_confidence'],
            'clarity_diff': abs(state.target_metrics['avg_confidence'] - 
                               state.current_metrics['avg_confidence']),
            'target_pos': state.target_metrics['avg_y_position'],
            'current_pos': state.current_metrics['avg_y_position'],
            'position_diff': abs(state.target_metrics['avg_y_position'] - 
                                state.current_metrics['avg_y_position']),
            'target_size': state.target_metrics['estimated_font_size'],
            'current_size': state.current_metrics.get('estimated_font_size', 0)
        }
    
    def _store_iteration(self, state: GraphState):
        """Store current iteration result"""
        iteration_result = {
            'iteration': state.iteration,
            'parameters': state.parameters.copy(),
            'metrics': state.current_metrics,
            'comparison': state.comparison_result,
            'video_path': str(state.video_path),
            'screenshot_path': str(state.screenshot_path)
        }
        state.all_iterations.append(iteration_result)
    
    def _empty_comparison(self) -> dict:
        """Return empty comparison result"""
        return {
            'clarity_score': 0,
            'position_score': 0,
            'size_score': 0,
            'overall_score': 0
        }
