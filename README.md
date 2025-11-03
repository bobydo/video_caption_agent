# AI Agent: Graph-Based Subtitle Improvement

An intelligent video subtitle optimization system that automatically generates Chinese subtitles and tunes font size and position to match a reference image (`chinese_sample.jpg`) using a graph-based node architecture.

## Purpose

This application fine-tunes Chinese subtitle appearance by:
- **Font Size Optimization**: Automatically adjusts subtitle font size to match target reference
- **Position Tuning**: Aligns subtitle vertical position with the reference image
- **Quality Assessment**: Uses OCR analysis to score clarity, position, and size accuracy

The system uses `chinese_sample.jpg` as the target reference to optimize subtitle rendering parameters through iterative improvement cycles.

## Quick Start

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

## Configuration (config.py)

The main tuning parameters are defined in `config.py`:

### Core Parameters
```python
max_iterations: int = 1              # Maximum optimization cycles
similarity: float = 95.0             # Score threshold to stop early (0-100%)
initial_font_scale: float = 0.25     # Starting font size (25% of detected size)
```

### Parameter Ranges
```python
font_size_range: [20, 24, 28, 32, 36, 40, 44, 48]     # Font sizes to test
stroke_width_range: [1, 2, 3]                          # Stroke widths to try
position_range: [0.60, 0.63, 0.65, 0.67, 0.70]       # Vertical positions (0-1)
```

### Scoring Weights
```python
comparison_weights: {
    'clarity': 0.4,      # 40% weight on OCR confidence
    'position': 0.3,     # 30% weight on position match  
    'size': 0.3          # 30% weight on size match
}
```

## Process Flow

### Main Script Process (`auto_improve_subtitles.py`)

```
START → File Validation → Config Setup → Audio Processing → Translation → Agent Execution
   ↓           ↓             ↓              ↓              ↓               ↓
Paths     Check Files   Load Config   Whisper STT   English→Chinese   Graph Resolver
Setup      Exist        Validate      Timestamps    Each Segment      Execute Nodes
   ↓           ↓             ↓              ↓              ↓               ↓
Target:    chinese       AgentConfig   Extract       translate_        SubtitleResolver
Output     sample.jpg    from config   audio with    tools.py for      Creates & executes:
Screenshots 10_second.mp4    .py        timestamps    each subtitle     - analyze_target
   ↓           ↓             ↓              ↓         segment text      - generate_video  
   ↓      Missing?       Valid          List of       Chinese text     - take_screenshot
   ↓        → EXIT       Parameters     segments      replaces original - analyze_current
   ↓                        ↓              ↓              ↓            - compare
   ↓                    Ready for      Ready for      Ready for        - adjust_parameters
   ↓                    Processing     Translation    Agent                   ↓
   ↓                        ↓              ↓              ↓            Final Results
   └────────────────────────┴──────────────┴──────────────┴──────────────────┘
                                                                              ↓
                                                                       Save Results
                                                                       Print Summary
                                                                       Complete
```

### AI Agent Graph Execution (graph-based architecture)

```
START → Analyze Target → Initialize Parameters → OPTIMIZATION LOOP
           ↓                        ↓                      ↓
     Target Metrics           Font Properties      Generate Video
    (analyze_target_         (resolver.py)        (generate_video_
     node.py)                                      node.py)
           ↓                        ↓                      ↓
     Reference Data          Initial Settings      Take Screenshot
                                   ↓             (take_screenshot_
                            ┌─────────────────────node.py)──────────┐
                            ↓                        ↓              ↓
                     Analyze Current ← OCR Analysis        Compare Metrics
                   (analyze_current_   (ocr_analyzer.py)  (compare_node.py)
                      node.py)                                     ↓
                            ↓                          EdgeConditions.check()
                   Current Metrics                         (graph.py)
                            ↓                                      ↓
                            └─────────────────────┬────────────────┘
                                                  ↓
                        ┌─── should_stop_success() (graph.py) → STOP_SUCCESS
                        ├─── should_stop_max_iterations() (graph.py) → STOP_MAX_ITERATIONS  
                        └─── should_continue() (graph.py) → Adjust Parameters → LOOP
                                                           (adjust_parameters_
                                                             node.py)
```

```python
# Future multi-agent state structure
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```

**Graph Components (core/):**
- **GraphState** (state.py): Agent memory containing metrics, parameters, iteration history
- **EdgeConditions** (graph.py): AI decision logic for stop/continue conditions
- **SubtitleResolver** (resolver.py): Agent orchestrator that executes the node graph
- **NodeType** (graph.py): Enumeration of all possible agent actions

### AI Agent Node Architecture
```
nodes/                                    # Agent Action Modules
├── base_node.py                         # Abstract base class for all agent actions
├── analyze_target_node.py              # PERCEPTION: Extract reference metrics
├── generate_video_node.py              # ACTION: Create video with parameters  
├── take_screenshot_node.py             # OBSERVATION: Capture result for analysis
├── analyze_current_node.py             # PERCEPTION: OCR analysis of current state
├── compare_node.py                     # REASONING: Score comparison with target
└── adjust_parameters_node.py           # LEARNING: Optimize parameters for next iteration

core/                                    # Agent Intelligence Framework  
├── state.py → GraphState               # MEMORY: Agent persistent state & history
├── graph.py → EdgeConditions           # DECISIONS: Stop/continue logic  
└── resolver.py → SubtitleResolver      # ORCHESTRATOR: Agent execution engine
```

**Agent Intelligence Pattern:**
- **PERCEPTION** nodes gather information (analyze_target, analyze_current)
- **ACTION** nodes modify the environment (generate_video, take_screenshot)  
- **REASONING** nodes evaluate performance (compare)
- **LEARNING** nodes improve behavior (adjust_parameters)
- **MEMORY** (GraphState) persists all data across iterations
- **DECISIONS** (EdgeConditions) determine when to stop or continue

## Directory Structure

### Output Folders

#### `output/` Directory
- **`10_second_1.mp4`**, **`10_second_2.mp4`**, etc. - Generated videos for each iteration
- **`iteration_results.json`** - Complete results data including:
  - Parameter configurations tested
  - Scoring metrics for each iteration
  - Best performing parameters
  - Execution timestamps and performance data

#### `screenshots/` Directory 
- **`iteration_1_screenshot.png`**, **`iteration_2_screenshot.png`**, etc.
- Screenshots captured from each generated video for OCR analysis
- Used for comparing current results with target reference image
- Helps visualize subtitle positioning and clarity improvements

### Core Files
```
├── auto_improve_subtitles.py    # Main execution script
├── config.py                    # Agent configuration parameters
├── chinese_sample.jpg           # Target reference image
├── 10_second.mp4               # Source video file
├── requirements.txt            # Python dependencies
├── screenshots                 # Agent observation data
├── output                      # Agent output artifacts
├── core/                       # AI Agent Framework
│   ├── state.py                # Agent Memory (GraphState)
│   ├── graph.py                # Agent Decision Logic (EdgeConditions)  
│   └── resolver.py             # Agent Orchestrator (SubtitleResolver)
└── utils/                      # Agent Capability Tools
    ├── ocr_analyzer.py         # Vision capability (EasyOCR)
    ├── subtitle_renderer.py    # Video generation capability
    ├── whisper_tools.py        # Audio processing capability  
    └── translate_tools.py      # Language capability (LLM)
```

**Key Steps:**
1. **Setup Phase**: Validate paths, check required files exist
2. **Audio Phase**: `whisper_tools.transcribe_with_timestamps()` → English segments with timing
3. **Translation Phase**: `translate_tools.translate_text()` → Convert each segment to Chinese
4. **Agent Phase**: `SubtitleResolver.resolve()` → Execute graph-based optimization
5. **Output Phase**: Save iteration results and print final summary

### AI Agent Workflow (Graph-Based Optimization)
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

### Scoring System
- **Clarity Score**: Based on OCR confidence of Chinese text recognition
- **Position Score**: Vertical position match with reference image
- **Size Score**: Font size similarity to target reference
- **Overall Score**: Weighted combination (configurable in `config.py`)

## Stop Conditions

The optimization loop terminates when:
1. **Success Threshold Reached**: Score ≥ configured threshold (default: 95%)
2. **Max Iterations**: Reached iteration limit (default: 1, configurable)
3. **No Chinese Text**: OCR fails to detect Chinese characters in result
4. **Critical Error**: File I/O errors or processing failures

## Technical Details

### Dependencies
- **faster-whisper**: Audio transcription
- **easyocr**: Optical character recognition
- **opencv-python**: Image processing
- **moviepy**: Video generation and editing
- **ollama**: Local LLM integration
- **requests**: API communication

### Supported Formats
- **Input Video**: MP4, AVI, MOV (any format supported by moviepy)
- **Reference Image**: JPG, PNG (processed by EasyOCR)
- **Output Video**: MP4 with embedded subtitles

### Future Enhancements
The current implementation is a single-agent pipeline. Future versions may implement:
- **Multi-Agent Architecture**: Using LangGraph message-based state management
- **Parallel Parameter Testing**: Concurrent optimization paths
- **Advanced Scoring**: Machine learning-based quality assessment

