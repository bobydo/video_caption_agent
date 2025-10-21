# 🤖 AI Agent: Graph-Based Subtitle Improvement

Automatically generates Chinese subtitles for videos using Whisper transcription, Ollama translation, and iterative optimization.

## **Features**

- 🎙️ **Whisper Transcription** - Auto-transcribe audio from video
- 🌐 **Ollama Translation** - Translate English → Chinese (llama3.1:8b)
- 🎬 **Dynamic Subtitles** - Multi-segment subtitles with timing
- 🔄 **Iterative Optimization** - Adjust font/position until target matched
- ✅ **Chinese Validation** - Exits early if no Chinese detected

## **Quick Start**

```powershell
cd D:\video-agent\agent
$env:PYTHONIOENCODING="utf-8"
python auto_improve_subtitles.py
```

**Prerequisites:**
- Ollama running with llama3.1:8b model
- Files: `chinese_sample.jpg` and `10_second.mp4` in agent folder

## **Architecture**

```
START → [Analyze Target] → LOOP → [Generate Video] 
                              ↓
                        [Take Screenshot]
                              ↓
                        [Analyze Current] ← Validate Chinese
                              ↓
                          [Compare]
                              ↓
                    ┌─── Score ≥ 95% → STOP
                    └─── Else → [Adjust] → LOOP
```

## **Configuration**

Edit `config.py`:

```python
max_iterations: int = 1              # Number of optimization iterations
success_threshold: float = 95.0      # Score to stop early
initial_font_scale: float = 0.35     # Font size (35% of detected)
font_size_range: [20-48]             # Font sizes to try
```

## **Output**

Files generated in:
- `output/10_second_*.mp4` - Generated videos
- `screenshots/iteration_*_screenshot.png` - Screenshots
- `output/iteration_results.json` - Results data

## **Node Reference**

| Node | Purpose |
|------|---------|
| **Analyze Target** | Extract metrics from chinese_sample.jpg |
| **Generate Video** | Create video with dynamic subtitles |
| **Take Screenshot** | Capture frame from video |
| **Analyze Current** | OCR + Chinese validation |
| **Compare** | Score vs target (clarity/position/size) |
| **Adjust Parameters** | Smart parameter tuning |

## **Stop Conditions**

1. **Success**: Score ≥ 95%
2. **Max Iterations**: Reached configured limit
3. **Error**: No Chinese characters detected

## **Future**
- The agent is a single-agent pipeline with:
- LangGraph Approach (Message-Based State) will be applied to multiple agent
```python
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

```