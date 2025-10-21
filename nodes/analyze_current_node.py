"""
Analyze Current Node - OCR analysis of current screenshot
"""

from nodes.base_node import BaseNode
from core.state import GraphState
from utils.ocr_analyzer import OCRAnalyzer


class AnalyzeCurrentNode(BaseNode):
    """Analyze current screenshot with OCR"""
    
    def __init__(self, ocr_analyzer: OCRAnalyzer):
        self.ocr = ocr_analyzer
    
    def execute(self, state: GraphState) -> GraphState:
        """Analyze current screenshot"""
        print(f"\n{'='*60}")
        print(f"🔍 NODE: Analyze Current Screenshot")
        print(f"{'='*60}")
        
        # OCR analysis
        if state.screenshot_path is None:
            raise ValueError("Screenshot path is None, cannot analyze")
        
        current_metrics = self.ocr.analyze_image(state.screenshot_path, verbose=True)
        
        # Validate that Chinese characters are present in the screenshot
        has_chinese = False
        if current_metrics.get('texts'):
            for text in current_metrics['texts']:
                # Check if text contains Chinese characters (U+4E00 to U+9FFF)
                if any('\u4e00' <= char <= '\u9fff' for char in text):
                    has_chinese = True
                    break
        
        if not has_chinese:
            print(f"\n{'❌'*30}")
            print("❌ ERROR: NO CHINESE CHARACTERS DETECTED IN SCREENSHOT!")
            print(f"{'❌'*30}")
            print("\n🔍 Detected texts:")
            for text in current_metrics.get('texts', []):
                print(f"   - '{text}'")
            print("\n💡 Possible issues:")
            print("   1. Subtitle rendering failed")
            print("   2. Font file not found or invalid")
            print("   3. Text position is off-screen")
            print("   4. Text color blends with background")
            print("\n⏹️  Stopping execution to prevent wasted iterations.")
            print(f"{'='*60}\n")
            
            # Set stop reason and exit
            state.stop_reason = "ERROR: No Chinese characters detected in screenshot"
            raise RuntimeError("No Chinese characters detected in generated subtitle. Please check subtitle rendering.")
        
        state.current_metrics = current_metrics
        return state
