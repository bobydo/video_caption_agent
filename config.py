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
    similarity: float = 95.0
    
    # Comparison weights (must sum to 1.0)
    # Controls how the system evaluates and scores the quality of generated subtitles
    comparison_weights: Dict[str, float] = field(default_factory=lambda: {
        'clarity': 0.4,      # 40% weight on OCR confidence
        'position': 0.3,     # 30% weight on position match
        'size': 0.3          # 30% weight on size match
    })
    
    # Parameter ranges to explore
    font_size_range: List[int] = field(default_factory=lambda: [20, 24, 28, 32, 36, 40, 44, 48])
    # 1 = Thin 1-pixel outline around each character
    # https://ink-and-brush.com/chinese-calligraphy-brush-strokes/
    stroke_width_range: List[int] = field(default_factory=lambda: [1, 2, 3])
    # Percentages of the video height measured from the top of the image
    # 0.60 = 60% down from the top (40% from bottom)
    position_range: List[float] = field(default_factory=lambda: [0.60, 0.63, 0.65, 0.67, 0.70])
    
    # Start with 35% of detected size (dynamically calculated from reference image)
    # Set 0.20 would likely result in more iterations but potentially higher accuracy.
    initial_font_scale: float = 0.25 
    
    # Font paths (in priority order)
    font_paths: List[str] = field(default_factory=lambda: [
        "C:/Windows/Fonts/msyhbd.ttc",  # Microsoft YaHei Bold (preferred)
        "C:/Windows/Fonts/msyh.ttc",    # Microsoft YaHei
        "C:/Windows/Fonts/simhei.ttf",  # SimHei
    ])
    
    # Translation configuration
    ollama_url: str = "http://localhost:11434/api/generate"
    # 1000 characters gives you plenty of room for complete sentences with proper punctuation. It's designed to handle even the longest, 
    # most complex sentences while ensuring complete context and proper sentence boundaries for high-quality translation.
    max_chunk_size: int = 1000
    translation_model: str = "llama3.1:8b"
    
    # Translation prompt configuration (easily customizable)
    source_language: str = "English"
    target_language: str = "Simplified Chinese"
    translation_instruction: str = ("Provide a natural, conversational translation while maintaining technical terms and accuracy. "
                                   "Only return the Chinese translation, nothing else")
    translation_prompt_template: str = "Please translate the following {source_language} text to {target_language}. {instruction}:\n\n{text}"
    
    translation_options: Dict[str, float] = field(default_factory=lambda: {
        "temperature": 0.1, # Temperature: 0.1 (Low = Consistent)
        "top_p": 0.9 # Top_p: 0.9 (High = Quality Focus)
    })
    
    # Sentence splitting configuration (now uses LLM for intelligent splitting)
    use_llm_sentence_splitting: bool = True  # Use LLM for smart sentence splitting
    sentence_split_fallback_pattern: str = r'(?<=[.!?;])\s+'  # Fallback regex if LLM fails
    sentence_split_prompt_template: str = ("Split the following text into separate sentences. "
                                          "Return only the sentences, one per line, with no numbering or extra text:\n\n{text}")
    sentence_split_options: Dict[str, float] = field(default_factory=lambda: {
        "temperature": 0.1,  # Low temperature for consistent splitting
        "top_p": 0.8         # Focus on high-probability words
    })
    
    def validate(self):
        """Validate configuration"""
        # Check weights sum to 1.0
        total_weight = sum(self.comparison_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Comparison weights must sum to 1.0, got {total_weight}")
        
        # Check ranges
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")
        
        if not (0 < self.similarity <= 100):
            raise ValueError("similarity must be between 0 and 100")
        
        return True

# Default configuration instance
DEFAULT_CONFIG = AgentConfig()
