# 🤖 AI Agent: Modular Architecture

## **Project Structure**

```
agent/
├── config.py                      ← All configuration in one place
├── auto_improve_subtitles.py      ← Main entry point (clean & simple)
│
├── core/                          ← Graph infrastructure
│   ├── __init__.py
│   ├── state.py                   ← GraphState data class
│   ├── graph.py                   ← NodeType enum, EdgeConditions
│   └── resolver.py                ← Orchestrates graph execution
│
├── nodes/                         ← Processing nodes (one class per file)
│   ├── __init__.py
│   ├── base_node.py               ← Abstract base class
│   ├── analyze_target_node.py     ← Extract metrics from target
│   ├── generate_video_node.py     ← Create video with subtitles
│   ├── take_screenshot_node.py    ← Capture frame
│   ├── analyze_current_node.py    ← OCR analysis
│   ├── compare_node.py            ← Score comparison
│   └── adjust_parameters_node.py  ← Smart parameter tuning
│
├── utils/                         ← Helper utilities
│   ├── __init__.py
│   ├── ocr_analyzer.py            ← EasyOCR wrapper class
│   └── subtitle_renderer.py       ← PIL rendering functions
│
├── output/                        ← Generated videos
├── screenshots/                   ← Analysis screenshots
│
├── chinese_sample.jpg             ← Reference image
├── 10_second.mp4                  ← Source video
│
├── README.md                      ← This file
└── run_agent.bat                  ← Quick run script
```

## **Clean Architecture Benefits**

✅ **Separated Concerns**: Each file has one clear responsibility  
✅ **Easy to Test**: Each node/util can be tested independently  
✅ **Easy to Extend**: Add new nodes without touching existing code  
✅ **Configuration Centralized**: All settings in `config.py`  
✅ **Class-Based**: Clean OOP design with inheritance  
✅ **Modular**: Import only what you need  

## **Configuration**

All configuration is in **`config.py`**:

```python
config = AgentConfig(
    max_iterations=7,              # Stop after N tries
    success_threshold=95.0,        # Score needed to succeed
    comparison_weights={           # How to weight scores
        'clarity': 0.4,           # 40% OCR confidence
        'position': 0.3,          # 30% position match
        'size': 0.3               # 30% size match
    },
    font_size_range=[28, 30, 32, 34, 36, 38, 40],
    stroke_width_range=[1, 2, 3],
    position_range=[0.60, 0.63, 0.65, 0.67, 0.70]
)
```

## **How to Run**

```powershell
cd D:\video-agent\agent
python auto_improve_subtitles.py
```

or double-click `run_agent.bat`

## **File Responsibilities**

### **config.py**
- `AgentConfig`: All configurable parameters
- Validation logic for configuration

### **core/state.py**
- `GraphState`: Data that flows through nodes
- Tracks iteration, metrics, parameters, results

### **core/graph.py**
- `NodeType`: Enum of all node types
- `EdgeConditions`: Logic for graph transitions

### **core/resolver.py**
- `SubtitleResolver`: Orchestrates graph execution
- Manages node sequence and stop conditions
- Saves results and prints summary

### **nodes/base_node.py**
- `BaseNode`: Abstract base class
- Defines `execute()` interface

### **nodes/analyze_target_node.py**
- `AnalyzeTargetNode`: Analyzes reference image
- Extracts target metrics using OCR

### **nodes/generate_video_node.py**
- `GenerateVideoNode`: Creates video with subtitles
- Uses MoviePy and PIL rendering

### **nodes/take_screenshot_node.py**
- `TakeScreenshotNode`: Captures frame from video
- Saves screenshot for analysis

### **nodes/analyze_current_node.py**
- `AnalyzeCurrentNode`: OCR analysis of screenshot
- Extracts current metrics

### **nodes/compare_node.py**
- `CompareNode`: Scores current vs target
- Calculates clarity, position, size scores
- Tracks best result

### **nodes/adjust_parameters_node.py**
- `AdjustParametersNode`: Smart parameter tuning
- Adjusts based on comparison scores

### **utils/ocr_analyzer.py**
- `OCRAnalyzer`: Wrapper for EasyOCR
- Reusable OCR analysis logic

### **utils/subtitle_renderer.py**
- `create_subtitle_image()`: PIL-based subtitle rendering
- Pure function for image generation

## **Adding New Nodes**

1. Create new file in `nodes/`
2. Inherit from `BaseNode`
3. Implement `execute(state) -> state`
4. Add to `nodes/__init__.py`
5. Wire into resolver

Example:

```python
# nodes/my_new_node.py
from nodes.base_node import BaseNode
from core.state import GraphState

class MyNewNode(BaseNode):
    def execute(self, state: GraphState) -> GraphState:
        print("🆕 NODE: My New Node")
        # Your logic here
        return state
```

## **Modifying Configuration**

Edit `config.py` or pass custom config in `auto_improve_subtitles.py`:

```python
config = AgentConfig(
    max_iterations=10,          # Try more times
    success_threshold=90.0,     # Lower threshold
    comparison_weights={
        'clarity': 0.5,         # More weight on clarity
        'position': 0.25,
        'size': 0.25
    }
)
```

## **Debugging**

Each node prints its execution:
```
============================================================
📸 NODE: Analyze Target Image
============================================================
  📝 Detected: '...' (confidence: 94.32%)
  ✅ Target Metrics Extracted
```

Check logs to see which node is executing and what it's doing.

## **Testing Individual Components**

```python
# Test OCR analyzer alone
from utils.ocr_analyzer import OCRAnalyzer
analyzer = OCRAnalyzer()
metrics = analyzer.analyze_image(Path("test.jpg"))

# Test subtitle renderer alone
from utils.subtitle_renderer import create_subtitle_image
img = create_subtitle_image("测试", 1920, 100, 32, 2, "font.ttc")

# Test single node
from nodes.analyze_target_node import AnalyzeTargetNode
node = AnalyzeTargetNode(target_path, analyzer)
new_state = node.execute(state)
```

## **Dependencies**

- **MoviePy**: Video processing
- **PIL/Pillow**: Image rendering
- **EasyOCR**: Chinese text detection
- **OpenCV**: Image operations

## **Key Concepts**

### **Node**
- Self-contained processing unit
- Takes state, returns state
- No side effects except logging

### **Edge**
- Conditional transition logic
- Determines when to continue/stop
- Implemented in `EdgeConditions` class

### **Resolver**
- Controls overall execution flow
- Manages node sequence
- Enforces stop conditions

### **State**
- Immutable data flow
- Passed between nodes
- Contains all context

---

**Clean, modular, maintainable code!** 🎉
