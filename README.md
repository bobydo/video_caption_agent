# 🤖 AI Agent: Graph-Based Subtitle Improvement

An intelligent video subtitle optimization system that automatically generates Chinese subtitles and tunes font size and position to match a reference image (`chinese_sample.jpg`) using a graph-based node architecture.

## 🎯 **Purpose**

This application fine-tunes Chinese subtitle appearance by:
- **Font Size Optimization**: Automatically adjusts subtitle font size to match target reference
- **Position Tuning**: Aligns subtitle vertical position with the reference image
- **Quality Assessment**: Uses OCR analysis to score clarity, position, and size accuracy

The system uses `chinese_sample.jpg` as the target reference to optimize subtitle rendering parameters through iterative improvement cycles.

## 🚀 **Quick Start**

```bash
# Install dependencies
pip install -r requirements.txt

# Run the agent
python auto_improve_subtitles.py
```

**Prerequisites:**
- Ollama running with a compatible Local LLM model (llama3.2:3b or similar)
- Input files: `chinese_sample.jpg` (reference) and `10_second.mp4` (video source)
- Python 3.8+ with required packages

## ⚙️ **Configuration (config.py)**

The main tuning parameters are defined in `config.py`:

### **Core Parameters**
```python
max_iterations: int = 1              # Maximum optimization cycles
success_threshold: float = 95.0      # Score threshold to stop early (0-100%)
initial_font_scale: float = 0.35     # Starting font size (35% of detected size)
```

### **Parameter Ranges**
```python
font_size_range: [20, 24, 28, 32, 36, 40, 44, 48]     # Font sizes to test
stroke_width_range: [1, 2, 3]                          # Stroke widths to try
position_range: [0.60, 0.63, 0.65, 0.67, 0.70]       # Vertical positions (0-1)
```

### **Scoring Weights**
```python
comparison_weights: {
    'clarity': 0.4,      # 40% weight on OCR confidence
    'position': 0.3,     # 30% weight on position match  
    'size': 0.3          # 30% weight on size match
}
```

## 🏗️ **Node-Based Architecture**

The application uses a single-agent pipeline with specialized nodes:

### **Core Process Flow**
```
START → Analyze Target → Generate Video → Take Screenshot 
           ↓                                    ↓
     Target Metrics              Analyze Current ← OCR Analysis
           ↓                                    ↓
     Font Properties                      Compare Metrics
                                               ↓
                                    ┌─── Score ≥ 95% or No Chinese found  → STOP
                                    └─── Else → Adjust Parameters → LOOP
```

### **Node Structure**
```
nodes/
├── base_node.py              # Abstract base class for all nodes
├── analyze_target_node.py    # Extract metrics from chinese_sample.jpg
├── generate_video_node.py    # Create video with current parameters
├── take_screenshot_node.py   # Capture frame from generated video
├── analyze_current_node.py   # OCR analysis of current screenshot
├── compare_node.py           # Score comparison with target
└── adjust_parameters_node.py # Smart parameter optimization
```

Each node inherits from `BaseNode` and implements:
- `execute(state)`: Main processing logic
- Input/output state management
- Error handling and logging

## 📁 **Directory Structure**

### **Output Folders**

#### **`output/` Directory**
- **`10_second_1.mp4`**, **`10_second_2.mp4`**, etc. - Generated videos for each iteration
- **`iteration_results.json`** - Complete results data including:
  - Parameter configurations tested
  - Scoring metrics for each iteration
  - Best performing parameters
  - Execution timestamps and performance data

#### **`screenshots/` Directory** 
- **`iteration_1_screenshot.png`**, **`iteration_2_screenshot.png`**, etc.
- Screenshots captured from each generated video for OCR analysis
- Used for comparing current results with target reference image
- Helps visualize subtitle positioning and clarity improvements

### **Core Files**
```
├── auto_improve_subtitles.py    # Main execution script
├── config.py                    # All configuration parameters
├── chinese_sample.jpg           # Target reference image
├── 10_second.mp4               # Source video file
├── requirements.txt            # Python dependencies
├── core/                       # Graph state management
│   ├── state.py                # GraphState class definition
│   ├── graph.py                # Node execution graph
│   └── resolver.py             # Main execution resolver
└── utils/                      # Helper utilities
    ├── ocr_analyzer.py         # EasyOCR integration
    ├── subtitle_renderer.py    # Video subtitle generation
    ├── whisper_tools.py        # Audio transcription
    └── translate_tools.py      # Text translation
```

## 🔄 **Process Loop**

### **Basic Workflow**
1. **Audio Processing**: Extract and transcribe audio using Whisper
2. **Translation**: Convert English text to Chinese using Ollama LLM
3. **Target Analysis**: Analyze `chinese_sample.jpg` to extract reference metrics
4. **Iterative Optimization**:
   - Generate video with current parameters
   - Take screenshot of result
   - Analyze current subtitle properties with OCR
   - Compare against target metrics (clarity, position, size)
   - Calculate composite score (weighted average)
   - If score < threshold: adjust parameters and repeat
   - If score ≥ threshold or max iterations reached: stop

### **Scoring System**
- **Clarity Score**: Based on OCR confidence of Chinese text recognition
- **Position Score**: Vertical position match with reference image
- **Size Score**: Font size similarity to target reference
- **Overall Score**: Weighted combination (configurable in `config.py`)

## 🛑 **Stop Conditions**

The optimization loop terminates when:
1. **Success Threshold Reached**: Score ≥ configured threshold (default: 95%)
2. **Max Iterations**: Reached iteration limit (default: 1, configurable)
3. **No Chinese Text**: OCR fails to detect Chinese characters in result
4. **Critical Error**: File I/O errors or processing failures

## 🔧 **Technical Details**

### **Dependencies**
- **faster-whisper**: Audio transcription
- **easyocr**: Optical character recognition
- **opencv-python**: Image processing
- **moviepy**: Video generation and editing
- **ollama**: Local LLM integration
- **requests**: API communication

### **Supported Formats**
- **Input Video**: MP4, AVI, MOV (any format supported by moviepy)
- **Reference Image**: JPG, PNG (processed by EasyOCR)
- **Output Video**: MP4 with embedded subtitles

### **Future Enhancements**
The current implementation is a single-agent pipeline. Future versions may implement:
- **Multi-Agent Architecture**: Using LangGraph message-based state management
- **Parallel Parameter Testing**: Concurrent optimization paths
- **Advanced Scoring**: Machine learning-based quality assessment

```python
# Future multi-agent state structure
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```