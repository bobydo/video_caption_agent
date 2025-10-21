from faster_whisper import WhisperModel

def transcribe_audio(video_path):
    """
    Transcribe audio from video and return full text
    
    Args:
        video_path: Path to video file
    
    Returns:
        str: Full transcribed text
    """
    model = WhisperModel("base", device="cpu")
    segments, _ = model.transcribe(video_path)
    text = " ".join([seg.text for seg in segments])
    return text.strip()


def transcribe_with_timestamps(video_path, language="zh"):
    """
    Transcribe audio from video and return segments with timestamps
    
    Args:
        video_path: Path to video file
        language: Language code (default: "zh" for Chinese)
    
    Returns:
        list: List of dicts with 'start', 'end', 'text' keys
    """
    model = WhisperModel("base", device="cpu")
    segments, info = model.transcribe(video_path, language=language)
    
    subtitle_segments = []
    for segment in segments:
        subtitle_segments.append({
            'start': segment.start,
            'end': segment.end,
            'text': segment.text.strip()
        })
    
    return subtitle_segments

