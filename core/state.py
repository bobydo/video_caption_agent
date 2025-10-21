"""
Graph State - Data that flows through the agent graph
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pathlib import Path


@dataclass
class GraphState:
    """State that flows through the graph nodes"""
    
    # Iteration tracking
    iteration: int = 0
    
    # Metrics
    target_metrics: Optional[Dict[str, Any]] = None
    current_metrics: Optional[Dict[str, Any]] = None
    comparison_result: Optional[Dict[str, Any]] = None
    
    # Current parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Best result tracking
    best_result: Optional[Dict[str, Any]] = None
    
    # File paths
    video_path: Optional[Path] = None
    screenshot_path: Optional[Path] = None
    
    # History
    all_iterations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Stop information
    stop_reason: Optional[str] = None
    
    # Test subtitle text (for single static subtitle)
    test_subtitle: str = "在你的桌面上不能使用手机"
    
    # Subtitle segments (for multi-segment dynamic subtitles)
    subtitle_segments: Optional[List[Dict[str, Any]]] = None
