"""
Take Screenshot Node - Captures frame from video
"""

from pathlib import Path
import cv2
from moviepy import VideoFileClip
from nodes.base_node import BaseNode
from core.state import GraphState


class TakeScreenshotNode(BaseNode):
    """Take screenshot from generated video for analysis"""
    
    def __init__(self, screenshots_dir: Path):
        self.screenshots_dir = screenshots_dir
    
    def execute(self, state: GraphState) -> GraphState:
        """Capture screenshot from video"""
        print(f"\n{'='*60}")
        print(f"📸 NODE: Take Screenshot")
        print(f"{'='*60}")
        
        video = VideoFileClip(str(state.video_path))
        
        # Take screenshot at middle of video
        screenshot_time = min(5.0, video.duration / 2)
        frame = video.get_frame(screenshot_time)
        
        if frame is None:
            raise ValueError("Failed to capture frame from video")
        
        # Save screenshot
        screenshot_path = self.screenshots_dir / f"iteration_{state.iteration}_screenshot.png"
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(screenshot_path), frame_bgr)
        
        video.close()
        
        state.screenshot_path = screenshot_path
        self.log(f"✅ Screenshot saved: {screenshot_path.name}")
        
        return state
