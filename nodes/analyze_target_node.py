"""
Analyze Target Node - Extracts metrics from reference image
"""

from pathlib import Path
from nodes.base_node import BaseNode
from core.state import GraphState
from utils.ocr_analyzer import OCRAnalyzer


class AnalyzeTargetNode(BaseNode):
    """Analyze target reference image to extract metrics"""
    
    def __init__(self, target_image: Path, ocr_analyzer: OCRAnalyzer):
        self.target_image = target_image
        self.ocr = ocr_analyzer
    
    def execute(self, state: GraphState) -> GraphState:
        """Extract metrics from target image"""
        print(f"\n{'='*60}")
        print(f"📸 NODE: Analyze Target Image")
        print(f"{'='*60}")
        
        # OCR analysis
        target_metrics = self.ocr.analyze_image(self.target_image, verbose=True)
        
        if not target_metrics['text_detected']:
            self.log("⚠️  No text detected in target image!")
            state.target_metrics = None
            return state
        
        # Print extracted metrics
        self.log(f"✅ Target Metrics Extracted:")
        self.log(f"  - Avg Confidence: {target_metrics['avg_confidence']:.2%}")
        self.log(f"  - Vertical Position: {target_metrics['avg_y_position']:.2%}")
        self.log(f"  - Estimated Font Size: {target_metrics['estimated_font_size']}px")
        
        # Use the BEST quality Chinese text (highest confidence Chinese text)
        if target_metrics['texts']:
            # Find text with highest confidence that contains Chinese characters
            best_chinese_text = None
            best_confidence = 0
            
            for i, text in enumerate(target_metrics['texts']):
                confidence = target_metrics['confidences'][i]
                # Check if text contains Chinese characters
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
                if has_chinese and confidence > best_confidence:
                    best_chinese_text = text
                    best_confidence = confidence
            
            # Use best Chinese text, or fall back to highest confidence text
            if best_chinese_text:
                state.test_subtitle = best_chinese_text
                self.log(f"  - Test Text (Chinese, {best_confidence:.2%}): '{state.test_subtitle}'")
            else:
                # Fall back to text with highest confidence
                max_conf_idx = target_metrics['confidences'].index(max(target_metrics['confidences']))
                state.test_subtitle = target_metrics['texts'][max_conf_idx]
                self.log(f"  - Test Text (fallback): '{state.test_subtitle}'")
        
        state.target_metrics = target_metrics
        
        return state
