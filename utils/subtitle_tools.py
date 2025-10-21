import srt
import datetime
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def test_subtitle_visibility():
    """Test function to create a simple video with visible Chinese subtitles"""
    print("🧪 Testing subtitle visibility...")
    
    # Try creating image-based text for Chinese characters
    chinese_text = "橙色中文字幕测试显示"
    
    try:
        # Method: Create text image using PIL with system fonts
        from PIL import Image, ImageDraw, ImageFont
        import os
        
        # Create text image using PIL with better font handling
        img_width, img_height = 640, 80
        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to find a system font that supports Chinese - prefer bold fonts
        font_size = 32  # Double the previous size from 16 to 32
        font = None
        font_paths_to_try = [
            "C:/Windows/Fonts/msyhbd.ttc",  # Microsoft YaHei Bold (preferred for visibility)
            "C:/Windows/Fonts/msyh.ttc",    # Microsoft YaHei (modern, clean)
            "C:/Windows/Fonts/simhei.ttf",  # SimHei (bold style)
            "C:/Windows/Fonts/simsun.ttc",  # SimSun (classic)
            "C:/Windows/Fonts/arial.ttf",   # Arial (fallback)
        ]
        
        for font_path in font_paths_to_try:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    # Test if font can render Chinese
                    test_bbox = draw.textbbox((0, 0), chinese_text, font=font)
                    if test_bbox[2] > 0:  # If width > 0, font can render the text
                        print(f"✅ Found working font: {font_path}")
                        break
                except Exception as fe:
                    print(f"Font {font_path} failed: {fe}")
                    continue
        
        if font is None:
            # Use default font - this may not render Chinese properly
            try:
                font = ImageFont.load_default()
                print("⚠️ Using default font - Chinese characters may not display correctly")
            except:
                font = None
        
        if font:
            # Get text dimensions
            try:
                bbox = draw.textbbox((0, 0), chinese_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Center the text
                x = (img_width - text_width) // 2
                y = (img_height - text_height) // 2
                
                # Better color scheme for subtitles - white with dark outline
                stroke_width = 2
                # Draw shadow/outline for better contrast
                for adj in range(-stroke_width, stroke_width+1):
                    for adj2 in range(-stroke_width, stroke_width+1):
                        if adj != 0 or adj2 != 0:  # Don't draw at center position
                            draw.text((x+adj, y+adj2), chinese_text, font=font, fill='#000000')  # Black shadow
                # Draw main text in white for maximum readability
                draw.text((x, y), chinese_text, font=font, fill='#FFFFFF')
                
                # Save as temporary image
                temp_img_path = "temp_subtitle.png"
                img.save(temp_img_path)
                
                # Create ImageClip from the text image
                from moviepy import ImageClip
                txt_clip = ImageClip(temp_img_path, duration=5)
                txt_clip = txt_clip.with_position(('center', 320))
                
                print("✅ Created Chinese text using PIL image method")
            except Exception as te:
                print(f"Text rendering failed: {te}")
                raise te
        else:
            raise Exception("No font available")
        
    except Exception as e:
        print(f"❌ PIL method failed: {e}")
        # Fallback to simple English text with better colors
        txt_clip = TextClip(
            text="Chinese Subtitle Test",
            font_size=16,
            color='white',
            stroke_color='black',
            stroke_width=2
        ).with_duration(5).with_position(('center', 320))
        
        print("⚠️ Using English fallback text")
    
    # Create a black background video
    from moviepy import ColorClip
    bg = ColorClip(size=(640, 480), color=(0, 0, 0), duration=5)
    
    # Composite
    test_video = CompositeVideoClip([bg, txt_clip])
    
    # Save test
    test_video.write_videofile("subtitle_test.mp4", fps=24)
    test_video.close()
    bg.close()
    txt_clip.close()
    
    # Clean up temp image if it exists
    try:
        import os
        if os.path.exists("temp_subtitle.png"):
            os.remove("temp_subtitle.png")
    except:
        pass
    
    print("✅ Test video created: subtitle_test.mp4")
    print("📍 Text should appear at 2/3 from top (1/3 from bottom) with WHITE color and black shadow")
    print("📝 Using Microsoft YaHei font for better Chinese character rendering")
    print("🎨 Improved contrast: white text with black shadow for better readability")
    return "subtitle_test.mp4"

def create_subtitles(video_path, zh_text):
    import os
    
    # Create output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create subtitle segments
    lines = zh_text.split("。")
    subtitles = []
    start = datetime.timedelta(seconds=0)
    step = 3
    for i, line in enumerate(lines):
        end = start + datetime.timedelta(seconds=step)
        subtitles.append(srt.Subtitle(index=i+1, start=start, end=end, content=line.strip()))
        start = end

    # Create SRT file
    srt_text = srt.compose(subtitles)
    filename = os.path.basename(video_path)
    srt_filename = filename.replace(".mp4", "_zh.srt")
    srt_path = os.path.join(output_dir, srt_filename)
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_text)
    
    # Create video with embedded Chinese subtitles
    output_filename = filename.replace(".mp4", "_with_zh_subtitles.mp4")
    output_video_path = os.path.join(output_dir, output_filename)
    
    # Load video
    video = VideoFileClip(video_path)
    video_duration = video.duration
    
    # Create text clips for Chinese subtitles
    text_clips = []
    print(f"Creating {len(subtitles)} subtitle clips...")
    
    for i, subtitle in enumerate(subtitles):
        content = subtitle.content.strip()
        if content and len(content) > 0:  # Only create clips for non-empty content
            start_time = subtitle.start.total_seconds()
            end_time = subtitle.end.total_seconds()
            
            print(f"Subtitle {i+1}: '{content[:50]}...' ({start_time:.1f}s - {end_time:.1f}s)")
            
            # Don't go beyond video duration
            if start_time >= video_duration:
                break
            if end_time > video_duration:
                end_time = video_duration
            
            duration = end_time - start_time
            if duration <= 0:
                continue
                
            # Use PIL-based Chinese text rendering for better support
            try:
                from PIL import Image, ImageDraw, ImageFont
                import os
                from moviepy import ImageClip
                
                # Create text image using PIL
                img_width, img_height = video.w, 100  # Use video width, 100px height for text
                img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                
                # Try to find a system font that supports Chinese - prefer bold fonts
                font_size = 32  # Double the previous size from 16 to 32
                font = None
                font_paths_to_try = [
                    "C:/Windows/Fonts/msyhbd.ttc",  # Microsoft YaHei Bold (preferred for visibility)
                    "C:/Windows/Fonts/msyh.ttc",    # Microsoft YaHei (modern, clean)
                    "C:/Windows/Fonts/simhei.ttf",  # SimHei (bold style)
                    "C:/Windows/Fonts/simsun.ttc",  # SimSun (classic)
                ]
                
                for font_path in font_paths_to_try:
                    if os.path.exists(font_path):
                        try:
                            font = ImageFont.truetype(font_path, font_size)
                            break
                        except:
                            continue
                
                if font is None:
                    font = ImageFont.load_default()
                
                # Get text dimensions and center it
                bbox = draw.textbbox((0, 0), content, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (img_width - text_width) // 2
                y = (img_height - text_height) // 2
                
                # Better color scheme - white text with black shadow for maximum readability
                stroke_width = 2
                for adj in range(-stroke_width, stroke_width+1):
                    for adj2 in range(-stroke_width, stroke_width+1):
                        if adj != 0 or adj2 != 0:
                            draw.text((x+adj, y+adj2), content, font=font, fill='#000000')  # Black shadow
                draw.text((x, y), content, font=font, fill='#FFFFFF')  # White main text
                
                # Save temporary image
                temp_img_path = f"temp_subtitle_{i}.png"
                img.save(temp_img_path)
                
                # Create ImageClip from the text image
                txt_clip = ImageClip(temp_img_path, duration=duration)
                txt_clip = txt_clip.with_start(start_time)
                txt_clip = txt_clip.with_position(('center', video.h * 2 // 3))
                
                text_clips.append(txt_clip)
                print(f"  ✅ Created PIL text clip for subtitle {i+1}: '{content[:20]}...'")
                
            except Exception as e:
                print(f"  ❌ PIL method failed for subtitle {i+1}: {e}")
                continue
    
    # Composite video with Chinese text overlays
    if text_clips:
        final_video = CompositeVideoClip([video] + text_clips)
    else:
        final_video = video
    
    # Write the final video with embedded Chinese subtitles
    final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
    
    # Clean up
    final_video.close()
    video.close()
    
    # Clean up temporary image files
    import glob
    temp_files = glob.glob("temp_subtitle_*.png")
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
        except:
            pass
    
    print(f"✅ Video exported to: {output_video_path}")
    print(f"✅ Subtitles saved to: {srt_path}")
    
    return srt_path
