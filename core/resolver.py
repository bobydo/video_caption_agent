"""
Resolver - Orchestrates the graph execution
"""

import json
from datetime import datetime
from pathlib import Path

from core.state import GraphState
from core.graph import EdgeConditions
from config import AgentConfig
from nodes.analyze_target_node import AnalyzeTargetNode
from nodes.generate_video_node import GenerateVideoNode
from nodes.take_screenshot_node import TakeScreenshotNode
from nodes.analyze_current_node import AnalyzeCurrentNode
from nodes.compare_node import CompareNode
from nodes.adjust_parameters_node import AdjustParametersNode


class SubtitleResolver:
    """Resolver that orchestrates the graph execution until problem solved"""
    
    def __init__(self, config: AgentConfig, 
                 analyze_target: AnalyzeTargetNode,
                 generate_video: GenerateVideoNode,
                 take_screenshot: TakeScreenshotNode,
                 analyze_current: AnalyzeCurrentNode,
                 compare: CompareNode,
                 adjust_parameters: AdjustParametersNode,
                 output_dir: Path,
                 subtitle_segments=None):
        self.config = config
        self.nodes = {
            'analyze_target': analyze_target,
            'generate_video': generate_video,
            'take_screenshot': take_screenshot,
            'analyze_current': analyze_current,
            'compare': compare,
            'adjust_parameters': adjust_parameters
        }
        self.output_dir = output_dir
        self.state = GraphState()
        self.state.subtitle_segments = subtitle_segments  # Set Whisper segments
    
    def resolve(self) -> GraphState:
        """Execute the graph until stop condition met"""
        print(f"\n{'='*60}")
        print(f"🤖 RESOLVER: Starting Graph Execution")
        print(f"{'='*60}")
        print(f"Configuration:")
        print(f"  - Max Iterations: {self.config.max_iterations}")
        print(f"  - Success Threshold: {self.config.success_threshold}%")
        print(f"  - Weights: {self.config.comparison_weights}")
        
        try:
            # STEP 1: Analyze target image (once)
            self.state = self.nodes['analyze_target'].execute(self.state)
            
            # Initialize parameters from target
            if self.state.target_metrics:
                # Scale down the detected font size to make it fit better
                detected_size = self.state.target_metrics['estimated_font_size']
                scaled_size = int(detected_size * self.config.initial_font_scale)
                
                self.state.parameters = {
                    'font_size': scaled_size,
                    'stroke_width': 2,
                    'position_pct': self.state.target_metrics['avg_y_position'],
                    'font_path': self.config.font_paths[0]
                }
            
            # STEP 2-7: Iterate until stop condition
            while EdgeConditions.should_continue(self.state, self.config):
                # Generate video
                self.state = self.nodes['generate_video'].execute(self.state)
                
                # Take screenshot
                self.state = self.nodes['take_screenshot'].execute(self.state)
                
                # Analyze current
                self.state = self.nodes['analyze_current'].execute(self.state)
                
                # Compare with target
                self.state = self.nodes['compare'].execute(self.state)
                
                # Check stop conditions via edges
                if EdgeConditions.should_stop_success(self.state, self.config):
                    score = self.state.comparison_result['overall_score']
                    self.state.stop_reason = f"Success! Score {score:.1f} >= {self.config.success_threshold}"
                    print(f"\n🎉 {self.state.stop_reason}")
                    break
                
                if EdgeConditions.should_stop_max_iterations(self.state, self.config):
                    self.state.stop_reason = f"Max iterations ({self.config.max_iterations}) reached"
                    print(f"\n⏹️  {self.state.stop_reason}")
                    break
                
                # Adjust parameters for next iteration
                self.state = self.nodes['adjust_parameters'].execute(self.state)
            
            print(f"\n{'='*60}")
            print(f"✅ RESOLVER: Graph Execution Complete")
            print(f"{'='*60}")
            
            return self.state
            
        except Exception as e:
            print(f"\n❌ RESOLVER ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.state.stop_reason = f"Error: {str(e)}"
            return self.state
    
    def save_results(self):
        """Save results to JSON file"""
        results_file = self.output_dir / "iteration_results.json"
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_to_native(obj):
            """Recursively convert numpy types to Python native types"""
            import numpy as np
            from pathlib import Path
            
            if isinstance(obj, Path):
                return str(obj)
            elif isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(item) for item in obj]
            elif isinstance(obj, tuple):
                return [convert_to_native(item) for item in obj]
            return obj
        
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'config': {
                'max_iterations': self.config.max_iterations,
                'success_threshold': self.config.success_threshold,
                'comparison_weights': self.config.comparison_weights
            },
            'target_metrics': convert_to_native(self.state.target_metrics),
            'all_iterations': convert_to_native(self.state.all_iterations),
            'best_result': convert_to_native(self.state.best_result),
            'stop_reason': self.state.stop_reason,
            'total_iterations': self.state.iteration
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved: {results_file}")
    
    def print_summary(self):
        """Print final summary"""
        print(f"\n{'='*60}")
        print(f"🏆 FINAL SUMMARY")
        print(f"{'='*60}")
        print(f"Total Iterations: {self.state.iteration}")
        print(f"Stop Reason: {self.state.stop_reason}")
        
        if self.state.best_result:
            best = self.state.best_result
            print(f"\nBest Result (Iteration {best['iteration']}):")
            print(f"  Overall Score: {best['comparison']['overall_score']:.1f}/100")
            print(f"  - Clarity: {best['comparison']['clarity_score']:.1f}/100")
            print(f"  - Position: {best['comparison']['position_score']:.1f}/100")
            print(f"  - Size: {best['comparison']['size_score']:.1f}/100")
            print(f"\nBest Parameters:")
            print(f"  - Font Size: {best['parameters']['font_size']}px")
            print(f"  - Stroke: {best['parameters']['stroke_width']}px")
            print(f"  - Position: {best['parameters']['position_pct']:.1%}")
            print(f"\nBest Video: {best['video_path']}")
        
        print(f"{'='*60}\n")
