"""
Configuration for AI Subtitle Agent
All configurable parameters in one place

Features:
- Whisper: Auto-transcribe audio from video
- Ollama: Translate English → Chinese (requires Ollama with llama3.1:8b)
- Dynamic Subtitles: Multi-segment subtitles with timing
- Iterative Optimization: Adjust font/position until 95% match
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AgentConfig:
    """Configuration for the AI subtitle improvement agent"""
    
    # Stop conditions
    max_iterations: int = 1
    success_threshold: float = 95.0
    
    # Comparison weights (must sum to 1.0)
    comparison_weights: Dict[str, float] = field(default_factory=lambda: {
        'clarity': 0.4,      # 40% weight on OCR confidence
        'position': 0.3,     # 30% weight on position match
        'size': 0.3          # 30% weight on size match
    })
    
    # Parameter ranges to explore
    font_size_range: List[int] = field(default_factory=lambda: [20, 24, 28, 32, 36, 40, 44, 48])
    stroke_width_range: List[int] = field(default_factory=lambda: [1, 2, 3])
    position_range: List[float] = field(default_factory=lambda: [0.60, 0.63, 0.65, 0.67, 0.70])
    
    # Initial font size scaling (multiply detected size by this factor)
    initial_font_scale: float = 0.35  # Start with 35% of detected size (~28px from 81px)
    
    # Font paths (in priority order)
    font_paths: List[str] = field(default_factory=lambda: [
        "C:/Windows/Fonts/msyhbd.ttc",  # Microsoft YaHei Bold (preferred)
        "C:/Windows/Fonts/msyh.ttc",    # Microsoft YaHei
        "C:/Windows/Fonts/simhei.ttf",  # SimHei
    ])
    
    def validate(self):
        """Validate configuration"""
        # Check weights sum to 1.0
        total_weight = sum(self.comparison_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Comparison weights must sum to 1.0, got {total_weight}")
        
        # Check ranges
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")
        
        if not (0 < self.success_threshold <= 100):
            raise ValueError("success_threshold must be between 0 and 100")
        
        return True


# Default configuration instance
DEFAULT_CONFIG = AgentConfig()
