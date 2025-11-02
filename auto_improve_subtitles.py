#!/usr/bin/env python3
"""
AI Agent: Auto-Improve Chinese Subtitles (Refactored)
====================================================
Clean, modular graph-based architecture

Structure:
- config.py: All configuration
- core/: Graph state, edges, resolver
- nodes/: Individual node implementations
- utils/: Helper functions (OCR, rendering)
"""

import sys
import importlib.util
from pathlib import Path
from config import AgentConfig
from utils.ocr_analyzer import OCRAnalyzer
from nodes.analyze_target_node import AnalyzeTargetNode
from nodes.generate_video_node import GenerateVideoNode
from nodes.take_screenshot_node import TakeScreenshotNode
from nodes.analyze_current_node import AnalyzeCurrentNode
from nodes.compare_node import CompareNode
from nodes.adjust_parameters_node import AdjustParametersNode
from core.resolver import SubtitleResolver

# Helper function to load modules from utils directory
def load_utils_module(module_name):
    r"""Load a module from the utils directory"""
    utils_path = Path(__file__).parent / "utils" / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, utils_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {module_name} from {utils_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load whisper and translate tools
whisper_tools = load_utils_module("whisper_tools")
translate_tools = load_utils_module("translate_tools")


def main():
    """Main execution"""
    print("="*60)
    print("🤖 AI AGENT: Graph-Based Subtitle Improvement")
    print("="*60)
    
    # Paths
    agent_dir = Path(__file__).parent
    target_image = agent_dir / "chinese_sample.jpg"
    source_video = agent_dir / "10_second.mp4"
    output_dir = agent_dir / "output"
    screenshots_dir = agent_dir / "screenshots"
    
    # Check files exist
    if not target_image.exists():
        print(f"❌ Target image not found: {target_image}")
        print("   Please copy chinese_sample.jpg to agent folder!")
        return
    
    if not source_video.exists():
        print(f"❌ Source video not found: {source_video}")
        print("   Please copy 10_second.mp4 to agent folder!")
        return
    
    # Load configuration from config.py (uses defaults from AgentConfig)
    config = AgentConfig()
    
    # Validate configuration
    config.validate()
    
    # Generate subtitles from video using Whisper
    print(f"\n{'='*60}")
    print("🎙️  WHISPER: Generating Subtitles from Audio")
    print(f"{'='*60}")
    print(f"🎙️  Transcribing audio with Whisper...")
    subtitle_segments = whisper_tools.transcribe_with_timestamps(str(source_video), language="en")  # Changed to "en" since audio is English
    
    print(f"✅ Found {len(subtitle_segments)} subtitle segments")
    
    # Translate each segment to Chinese
    print(f"\n{'='*60}")
    print("🌐 TRANSLATION: English → Chinese")
    print(f"{'='*60}")
    
    for i, seg in enumerate(subtitle_segments, 1):
        english_text = seg['text']
        print(f"\n   Segment {i}/{len(subtitle_segments)}: {english_text}")
        
        # Translate to Chinese
        chinese_text = translate_tools.translate_text(english_text)
        seg['text'] = chinese_text  # Replace with Chinese translation
        seg['original_text'] = english_text  # Keep original for reference
        
        print(f"   ✅ Translated: {chinese_text}")
    
    print(f"\n{'='*60}")
    print("✅ All segments translated to Chinese")
    print(f"{'='*60}")
    for i, seg in enumerate(subtitle_segments[:3], 1):
        print(f"   {i}. [{seg['start']:.2f}s - {seg['end']:.2f}s]: {seg['text']}")
    if len(subtitle_segments) > 3:
        print(f"   ... and {len(subtitle_segments) - 3} more segments")
    
    # Create shared utilities
    ocr_analyzer = OCRAnalyzer()
    
    # Create nodes
    analyze_target = AnalyzeTargetNode(target_image, ocr_analyzer)
    generate_video = GenerateVideoNode(source_video, output_dir, screenshots_dir)
    take_screenshot = TakeScreenshotNode(screenshots_dir)
    analyze_current = AnalyzeCurrentNode(ocr_analyzer)
    compare = CompareNode(config)
    adjust_parameters = AdjustParametersNode(config)
    
    # Create resolver
    resolver = SubtitleResolver(
        config=config,
        analyze_target=analyze_target,
        generate_video=generate_video,
        take_screenshot=take_screenshot,
        analyze_current=analyze_current,
        compare=compare,
        adjust_parameters=adjust_parameters,
        output_dir=output_dir,
        subtitle_segments=subtitle_segments  # Pass Whisper segments
    )
    
    # Execute graph
    final_state = resolver.resolve()
    
    # Save results
    resolver.save_results()
    
    # Print summary
    resolver.print_summary()
    
    print("✅ Agent execution complete!")


if __name__ == "__main__":
    main()
