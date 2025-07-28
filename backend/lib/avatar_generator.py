"""
Simplified Avatar Video Generation System
Using free and open-source tools to create talking avatar videos
"""

import os
import tempfile
import subprocess
import uuid
from pathlib import Path
import cv2
import numpy as np
from pydub import AudioSegment
import base64
import logging

logger = logging.getLogger(__name__)

class AvatarVideoGenerator:
    def __init__(self):
        self.assets_dir = Path("/app/assets")
        self.temp_dir = Path("/app/tmp/avatar_videos")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure we have a default avatar image
        self.ensure_default_avatar()
    
    def ensure_default_avatar(self):
        """Create a simple default avatar image if none exists"""
        avatar_path = self.assets_dir / "default-avatar.jpg"
        if not avatar_path.exists():
            self.create_default_avatar(str(avatar_path))
    
    def create_default_avatar(self, output_path):
        """Create a simple avatar image using OpenCV"""
        # Create a 512x512 image with a simple avatar
        img = np.ones((512, 512, 3), dtype=np.uint8) * 240  # Light background
        
        # Draw a simple face
        center = (256, 256)
        
        # Face circle
        cv2.circle(img, center, 180, (255, 220, 177), -1)  # Skin color
        
        # Eyes
        cv2.circle(img, (200, 200), 25, (0, 0, 0), -1)  # Left eye
        cv2.circle(img, (312, 200), 25, (0, 0, 0), -1)  # Right eye
        
        # Eye whites
        cv2.circle(img, (200, 200), 20, (255, 255, 255), -1)
        cv2.circle(img, (312, 200), 20, (255, 255, 255), -1)
        
        # Pupils
        cv2.circle(img, (200, 200), 8, (0, 0, 0), -1)
        cv2.circle(img, (312, 200), 8, (0, 0, 0), -1)
        
        # Nose
        pts = np.array([[256, 220], [246, 260], [266, 260]], np.int32)
        cv2.fillPoly(img, [pts], (255, 200, 150))
        
        # Mouth (closed)
        cv2.ellipse(img, (256, 320), (40, 15), 0, 0, 180, (200, 100, 100), -1)
        
        # Save the image
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, img)
        logger.info(f"Created default avatar at {output_path}")
    
    def audio_base64_to_file(self, audio_base64: str, output_path: str):
        """Convert base64 audio to file"""
        try:
            # Decode base64 audio
            audio_data = base64.b64decode(audio_base64)
            
            # Write to temporary file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            # Convert to WAV format for better compatibility
            wav_path = output_path.replace('.mp3', '.wav').replace('.m4a', '.wav')
            audio = AudioSegment.from_file(output_path)
            audio.export(wav_path, format="wav")
            
            return wav_path
        except Exception as e:
            logger.error(f"Error converting audio: {str(e)}")
            raise
    
    def create_basic_talking_video(self, avatar_image_path: str, audio_path: str, output_path: str):
        """Create a basic talking avatar video using simple animation"""
        try:
            # Load the avatar image
            avatar = cv2.imread(avatar_image_path)
            if avatar is None:
                raise ValueError(f"Could not load avatar image from {avatar_image_path}")
            
            # Get audio duration
            audio = AudioSegment.from_file(audio_path)
            duration_seconds = len(audio) / 1000.0
            
            # Video parameters
            fps = 30
            total_frames = int(duration_seconds * fps)
            height, width = avatar.shape[:2]
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Generate frames with simple mouth animation
            for frame_num in range(total_frames):
                current_frame = avatar.copy()
                
                # Simple mouth animation based on frame number
                # This creates a basic opening/closing mouth effect
                mouth_open_factor = abs(np.sin(frame_num * 0.5)) * 0.5 + 0.2
                
                # Animate mouth area (simple approach)
                mouth_center = (width // 2, int(height * 0.625))  # Approximate mouth position
                mouth_width = int(40 * (1 + mouth_open_factor))
                mouth_height = int(15 * (1 + mouth_open_factor * 2))
                
                # Draw animated mouth
                cv2.ellipse(current_frame, mouth_center, (mouth_width, mouth_height), 
                           0, 0, 180, (150, 80, 80), -1)
                
                # Add slight head movement
                shift_x = int(5 * np.sin(frame_num * 0.1))
                shift_y = int(3 * np.cos(frame_num * 0.15))
                
                # Apply slight movement (simple translation)
                M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
                current_frame = cv2.warpAffine(current_frame, M, (width, height))
                
                video_writer.write(current_frame)
            
            video_writer.release()
            
            # Combine video with audio using ffmpeg
            final_output = output_path.replace('.mp4', '_final.mp4')
            self.combine_video_audio(output_path, audio_path, final_output)
            
            return final_output
            
        except Exception as e:
            logger.error(f"Error creating talking video: {str(e)}")
            raise
    
    def combine_video_audio(self, video_path: str, audio_path: str, output_path: str):
        """Combine video and audio using ffmpeg"""
        try:
            cmd = [
                'ffmpeg', '-y',  # -y to overwrite output file
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',  # End when shortest input ends
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise RuntimeError(f"FFmpeg failed: {result.stderr}")
            
            logger.info(f"Successfully combined video and audio: {output_path}")
            
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timeout")
            raise RuntimeError("Video generation timed out")
        except Exception as e:
            logger.error(f"Error combining video and audio: {str(e)}")
            raise
    
    def generate_avatar_video(self, audio_base64: str, avatar_image_path: str = None):
        """Main method to generate avatar video from base64 audio"""
        try:
            # Generate unique ID for this request
            request_id = str(uuid.uuid4())[:8]
            
            # Use default avatar if none provided
            if avatar_image_path is None:
                avatar_image_path = str(self.assets_dir / "default-avatar.jpg")
            
            # Create temporary files
            temp_audio_path = str(self.temp_dir / f"audio_{request_id}.mp3")
            temp_video_path = str(self.temp_dir / f"video_{request_id}.mp4")
            
            # Convert audio from base64 to file
            wav_audio_path = self.audio_base64_to_file(audio_base64, temp_audio_path)
            
            # Generate the talking video
            final_video_path = self.create_basic_talking_video(
                avatar_image_path, wav_audio_path, temp_video_path
            )
            
            # Get video duration before cleanup
            duration_seconds = self.get_video_duration(final_video_path)
            
            # Convert video to base64 for return
            with open(final_video_path, 'rb') as video_file:
                video_base64 = base64.b64encode(video_file.read()).decode('utf-8')
            
            # Cleanup temporary files
            self.cleanup_temp_files([temp_audio_path, wav_audio_path, temp_video_path, final_video_path])
            
            return {
                "video_base64": video_base64,
                "duration_seconds": duration_seconds,
                "request_id": request_id
            }
            
        except Exception as e:
            logger.error(f"Error generating avatar video: {str(e)}")
            raise
    
    def get_video_duration(self, video_path: str):
        """Get video duration in seconds"""
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = frame_count / fps if fps > 0 else 0
            cap.release()
            return duration
        except:
            return 0
    
    def cleanup_temp_files(self, file_paths):
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not cleanup file {file_path}: {str(e)}")

# Global instance
avatar_generator = AvatarVideoGenerator()