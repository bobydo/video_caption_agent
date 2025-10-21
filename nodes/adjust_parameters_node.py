"""
Adjust Parameters Node - Smart parameter tuning
"""

import random
from nodes.base_node import BaseNode
from core.state import GraphState
from config import AgentConfig


class AdjustParametersNode(BaseNode):
    """Adjust parameters based on comparison results"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
    
    def execute(self, state: GraphState) -> GraphState:
        """Adjust parameters for next iteration"""
        print(f"\n{'='*60}")
        print(f"🔧 NODE: Adjust Parameters")
        print(f"{'='*60}")
        
        prev_params = state.parameters.copy()
        
        # Adjust font size based on size score
        new_font_size = self._adjust_font_size(state, prev_params)
        
        # Adjust position based on position score
        new_position = self._adjust_position(state, prev_params)
        
        # Adjust stroke width
        new_stroke = random.choice(self.config.stroke_width_range)
        
        # Update parameters
        state.parameters = {
            'font_size': new_font_size,
            'stroke_width': new_stroke,
            'position_pct': new_position,
            'font_path': prev_params['font_path']
        }
        
        # Log changes
        self.log("Adjusted parameters for next iteration:")
        self.log(f"  - Font Size: {prev_params['font_size']}px → {new_font_size}px")
        self.log(f"  - Position: {prev_params['position_pct']:.1%} → {new_position:.1%}")
        self.log(f"  - Stroke: {prev_params['stroke_width']}px → {new_stroke}px")
        
        return state
    
    def _adjust_font_size(self, state: GraphState, prev_params: dict) -> int:
        """Adjust font size based on size score"""
        if state.comparison_result['size_score'] < 90:
            variations = [
                prev_params['font_size'] - 2,
                prev_params['font_size'] + 2,
            ]
            valid_variations = [f for f in variations if f in self.config.font_size_range]
            return random.choice(valid_variations) if valid_variations else prev_params['font_size']
        return prev_params['font_size']
    
    def _adjust_position(self, state: GraphState, prev_params: dict) -> float:
        """Adjust position based on position score"""
        if state.comparison_result['position_score'] < 90:
            variations = [
                prev_params['position_pct'] - 0.02,
                prev_params['position_pct'] + 0.02,
            ]
            valid_variations = [p for p in variations if 0.5 <= p <= 0.8]
            return random.choice(valid_variations) if valid_variations else prev_params['position_pct']
        return prev_params['position_pct']
