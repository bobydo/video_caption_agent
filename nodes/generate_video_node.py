"""
Generate Video Node - Creates video with subtitles
"""

from pathlib import Path
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip
from nodes.base_node import BaseNode
from core.state import GraphState
from utils.subtitle_renderer import create_subtitle_image


class GenerateVideoNode(BaseNode):
    """Generate video with Chinese subtitles using current parameters"""
    
    def __init__(self, source_video: Path, output_dir: Path, screenshots_dir: Path):
        self.source_video = source_video
        self.output_dir = output_dir
        self.screenshots_dir = screenshots_dir
    
    def execute(self, state: GraphState) -> GraphState:
        """Generate video with current subtitle parameters"""
        state.iteration += 1
        
        print(f"\n{'='*60}")
        print(f"🎬 NODE: Generate Video (Iteration {state.iteration})")
        print(f"{'='*60}")
        self.log(f"Font Size: {state.parameters['font_size']}px")
        self.log(f"Stroke Width: {state.parameters['stroke_width']}px")
        self.log(f"Position: {state.parameters['position_pct']:.1%}")
        
        # Load video
        video = VideoFileClip(str(self.source_video))
        
        # Create subtitle clips based on whether we have segments or single subtitle
        if state.subtitle_segments:
            # Multi-segment subtitles (dynamic)
            self.log(f"Creating {len(state.subtitle_segments)} subtitle segments...")
            subtitle_clips = self._create_multi_segment_subtitles(
                video, state.subtitle_segments, state.parameters, state.iteration
            )
        else:
            # Single static subtitle (legacy mode)
            subtitle_clips = [self._create_single_subtitle(
                video, state.test_subtitle, state.parameters, state.iteration
            )]
        
        # Composite video with all subtitle clips
        final_video = CompositeVideoClip([video] + subtitle_clips)
        
        # Output path
        output_path = self.output_dir / f"10_second_{state.iteration}.mp4"
        self.log(f"💾 Saving: {output_path.name}")
        
        # Write video
        final_video.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            fps=video.fps,
            logger=None
        )
        
        # Cleanup
        video.close()
        final_video.close()
        
        state.video_path = output_path
        return state
    
    def _create_single_subtitle(self, video, text, parameters, iteration):
        """Create a single static subtitle for entire video duration"""
        subtitle_img = create_subtitle_image(
            text=text,
            width=video.w,
            height=100,
            font_size=parameters['font_size'],
            stroke_width=parameters['stroke_width'],
            font_path=parameters['font_path']
        )
        
        # Save temporary image
        temp_img_path = self.screenshots_dir / f"temp_subtitle_{iteration}.png"
        subtitle_img.save(temp_img_path)
        
        # Create ImageClip
        txt_clip = ImageClip(str(temp_img_path), duration=video.duration)
        txt_clip = txt_clip.with_start(0)
        txt_clip = txt_clip.with_position(
            ('center', int(video.h * parameters['position_pct']))
        )
        
        return txt_clip
    
    def _create_multi_segment_subtitles(self, video, segments, parameters, iteration):
        """Create multiple subtitle clips with different start/end times"""
        subtitle_clips = []
        
        for i, segment in enumerate(segments):
            # Create subtitle image for this segment
            subtitle_img = create_subtitle_image(
                text=segment['text'],
                width=video.w,
                height=100,
                font_size=parameters['font_size'],
                stroke_width=parameters['stroke_width'],
                font_path=parameters['font_path']
            )
            
            # Save temporary image
            temp_img_path = self.screenshots_dir / f"temp_subtitle_{iteration}_seg{i}.png"
            subtitle_img.save(temp_img_path)
            
            # Calculate duration
            duration = segment['end'] - segment['start']
            
            # Create ImageClip with specific timing
            txt_clip = ImageClip(str(temp_img_path), duration=duration)
            txt_clip = txt_clip.with_start(segment['start'])
            txt_clip = txt_clip.with_position(
                ('center', int(video.h * parameters['position_pct']))
            )
            
            subtitle_clips.append(txt_clip)
        
        return subtitle_clips
