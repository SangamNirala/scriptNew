"""
Enhanced Avatar Video Generation System
Supports both user-uploaded images and AI-generated avatars
with context-aware background generation
"""

import os
import sys
import tempfile
import subprocess
import uuid
from pathlib import Path
import cv2
import numpy as np
from pydub import AudioSegment
import base64
import logging
from typing import Optional, Dict, Any, List
import asyncio
import concurrent.futures
from PIL import Image, ImageDraw, ImageFont
import json
import re

logger = logging.getLogger(__name__)

class EnhancedAvatarGenerator:
    def __init__(self):
        self.assets_dir = Path("/app/assets")
        self.temp_dir = Path("/app/tmp/avatar_videos")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.sadtalker_dir = Path("/app/SadTalker")
        
        # Check if SadTalker is available
        self.sadtalker_available = self.check_sadtalker_availability()
        
        # Initialize AI models
        self.setup_ai_models()
        
        # Ensure we have default resources
        self.ensure_default_resources()
    
    def check_sadtalker_availability(self) -> bool:
        """Check if SadTalker is properly installed and available"""
        try:
            if not self.sadtalker_dir.exists():
                return False
            
            # Check if required files exist
            required_files = [
                self.sadtalker_dir / "inference.py",
                self.sadtalker_dir / "checkpoints"
            ]
            
            for file_path in required_files:
                if not file_path.exists():
                    logger.warning(f"SadTalker file not found: {file_path}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking SadTalker availability: {str(e)}")
            return False
    
    def setup_ai_models(self):
        """Initialize AI models for avatar and background generation"""
        try:
            # Try to import and setup diffusion models for background generation
            try:
                from diffusers import StableDiffusionPipeline
                # We'll implement this later when we have the models
                self.bg_generator_available = False
                logger.info("Background generation models not yet initialized")
            except ImportError:
                self.bg_generator_available = False
                logger.warning("Diffusion models not available, using fallback background generation")
                
        except Exception as e:
            logger.error(f"Error setting up AI models: {str(e)}")
            self.bg_generator_available = False
    
    def ensure_default_resources(self):
        """Create default avatar and background resources"""
        # Create default avatar
        default_avatar_path = self.assets_dir / "default-avatar.jpg"
        if not default_avatar_path.exists():
            self.create_realistic_default_avatar(str(default_avatar_path))
        
        # Create default backgrounds
        self.create_default_backgrounds()
    
    def create_realistic_default_avatar(self, output_path: str):
        """Create a more realistic default avatar using improved graphics"""
        # Create a higher resolution image
        img = np.ones((512, 512, 3), dtype=np.uint8) * 245  # Light background
        
        # Create a more realistic face
        center = (256, 256)
        
        # Face oval (more realistic shape)
        face_axes = (160, 180)
        cv2.ellipse(img, center, face_axes, 0, 0, 360, (255, 220, 177), -1)
        
        # Add face shading for depth
        cv2.ellipse(img, center, (face_axes[0]-10, face_axes[1]-10), 0, 0, 360, (245, 210, 167), -1)
        
        # Eyes (more realistic)
        left_eye_center = (200, 200)
        right_eye_center = (312, 200)
        
        # Eye whites
        cv2.ellipse(img, left_eye_center, (30, 20), 0, 0, 360, (255, 255, 255), -1)
        cv2.ellipse(img, right_eye_center, (30, 20), 0, 0, 360, (255, 255, 255), -1)
        
        # Iris
        cv2.circle(img, left_eye_center, 15, (70, 130, 180), -1)  # Blue iris
        cv2.circle(img, right_eye_center, 15, (70, 130, 180), -1)
        
        # Pupils
        cv2.circle(img, left_eye_center, 8, (0, 0, 0), -1)
        cv2.circle(img, right_eye_center, 8, (0, 0, 0), -1)
        
        # Eye highlights
        cv2.circle(img, (left_eye_center[0]+3, left_eye_center[1]-3), 3, (255, 255, 255), -1)
        cv2.circle(img, (right_eye_center[0]+3, right_eye_center[1]-3), 3, (255, 255, 255), -1)
        
        # Eyebrows
        cv2.ellipse(img, (left_eye_center[0], left_eye_center[1]-25), (25, 8), 0, 0, 180, (101, 67, 33), -1)
        cv2.ellipse(img, (right_eye_center[0], right_eye_center[1]-25), (25, 8), 0, 0, 180, (101, 67, 33), -1)
        
        # Nose (more realistic shape)
        nose_pts = np.array([[256, 220], [248, 250], [256, 260], [264, 250]], np.int32)
        cv2.fillPoly(img, [nose_pts], (245, 200, 150))
        
        # Nostrils
        cv2.ellipse(img, (250, 255), (3, 6), 0, 0, 360, (200, 150, 100), -1)
        cv2.ellipse(img, (262, 255), (3, 6), 0, 0, 360, (200, 150, 100), -1)
        
        # Mouth (more realistic)
        mouth_center = (256, 320)
        cv2.ellipse(img, mouth_center, (25, 8), 0, 0, 360, (180, 100, 100), -1)
        cv2.ellipse(img, mouth_center, (20, 5), 0, 0, 360, (120, 60, 60), -1)
        
        # Hair (simple)
        hair_pts = np.array([[100, 100], [412, 100], [380, 180], [132, 180]], np.int32)
        cv2.fillPoly(img, [hair_pts], (101, 67, 33))
        
        # Save the image
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, img)
        logger.info(f"Created realistic default avatar at {output_path}")
    
    def create_default_backgrounds(self):
        """Create default background images for different contexts"""
        backgrounds_dir = self.assets_dir / "backgrounds"
        backgrounds_dir.mkdir(exist_ok=True)
        
        # Create different background types
        backgrounds = {
            "office": (240, 240, 255),  # Light blue
            "nature": (200, 255, 200),  # Light green
            "studio": (250, 250, 250),  # Light gray
            "tech": (220, 220, 240),    # Light purple
            "education": (255, 250, 200) # Light yellow
        }
        
        for bg_name, color in backgrounds.items():
            bg_path = backgrounds_dir / f"{bg_name}.jpg"
            if not bg_path.exists():
                self.create_gradient_background(str(bg_path), color)
    
    def create_gradient_background(self, output_path: str, base_color: tuple):
        """Create a gradient background image"""
        img = np.ones((512, 512, 3), dtype=np.uint8)
        
        # Create gradient effect
        for y in range(512):
            factor = y / 512.0
            color = tuple(int(base_color[i] * (0.8 + 0.2 * factor)) for i in range(3))
            img[y, :] = color
        
        cv2.imwrite(output_path, img)
        logger.info(f"Created gradient background at {output_path}")
    
    def generate_ai_avatar_image(self, description: str = "professional person") -> str:
        """Generate an AI avatar image (placeholder implementation)"""
        # For now, create a variation of the default avatar
        # In a full implementation, this would use AI image generation
        
        request_id = str(uuid.uuid4())[:8]
        avatar_path = str(self.temp_dir / f"ai_avatar_{request_id}.jpg")
        
        # Create a slightly different version of the default avatar
        self.create_realistic_default_avatar(avatar_path)
        
        # Add some variation based on description
        img = cv2.imread(avatar_path)
        
        # Simple variations based on description
        if "professional" in description.lower():
            # Add suit-like collar
            cv2.rectangle(img, (200, 450), (312, 512), (50, 50, 100), -1)
        elif "casual" in description.lower():
            # Add casual shirt
            cv2.rectangle(img, (200, 450), (312, 512), (100, 150, 200), -1)
        
        cv2.imwrite(avatar_path, img)
        logger.info(f"Generated AI avatar at {avatar_path}")
        return avatar_path
    
    def parse_script_for_backgrounds(self, script: str) -> List[Dict[str, Any]]:
        """Parse script into segments and determine appropriate backgrounds"""
        # Split script into sentences
        sentences = re.split(r'[.!?]+', script)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        segments = []
        for i, sentence in enumerate(sentences):
            # Analyze sentence content to determine background
            bg_type = self.determine_background_type(sentence)
            
            segments.append({
                "text": sentence,
                "background_type": bg_type,
                "start_time": i * 3,  # Approximate timing
                "duration": 3
            })
        
        return segments
    
    def determine_background_type(self, text: str) -> str:
        """Determine appropriate background type based on text content"""
        text_lower = text.lower()
        
        # Keywords for different background types
        keywords = {
            "office": ["business", "meeting", "work", "office", "corporate", "professional"],
            "nature": ["nature", "outdoor", "forest", "mountain", "ocean", "natural"],
            "tech": ["technology", "computer", "digital", "software", "tech", "innovation"],
            "education": ["learn", "education", "school", "study", "knowledge", "teach"],
            "studio": ["presentation", "news", "announcement", "formal"]
        }
        
        # Find best match
        best_match = "studio"  # default
        max_score = 0
        
        for bg_type, words in keywords.items():
            score = sum(1 for word in words if word in text_lower)
            if score > max_score:
                max_score = score
                best_match = bg_type
        
        return best_match
    
    def generate_background_image(self, background_type: str, text_context: str) -> str:
        """Generate or select background image based on context"""
        # For now, use pre-created backgrounds
        # In a full implementation, this would use AI image generation
        
        backgrounds_dir = self.assets_dir / "backgrounds"
        bg_path = backgrounds_dir / f"{background_type}.jpg"
        
        if bg_path.exists():
            return str(bg_path)
        else:
            # Fallback to studio background
            return str(backgrounds_dir / "studio.jpg")
    
    def create_talking_video_with_sadtalker(self, image_path: str, audio_path: str, output_path: str) -> str:
        """Create talking video using SadTalker"""
        try:
            if not self.sadtalker_available:
                raise RuntimeError("SadTalker is not available")
            
            # Prepare SadTalker command
            cmd = [
                sys.executable, "inference.py",
                "--driven_audio", audio_path,
                "--source_image", image_path,
                "--result_dir", str(self.temp_dir),
                "--still",
                "--preprocess", "crop",
                "--size", "256"
            ]
            
            # Run SadTalker
            result = subprocess.run(
                cmd,
                cwd=str(self.sadtalker_dir),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                logger.error(f"SadTalker error: {result.stderr}")
                raise RuntimeError(f"SadTalker failed: {result.stderr}")
            
            # Find the generated video
            result_dirs = [d for d in self.temp_dir.iterdir() if d.is_dir()]
            if result_dirs:
                latest_dir = max(result_dirs, key=lambda x: x.stat().st_mtime)
                video_files = list(latest_dir.glob("*.mp4"))
                if video_files:
                    generated_video = video_files[0]
                    # Move to our output path
                    subprocess.run(["mv", str(generated_video), output_path], check=True)
                    return output_path
            
            raise RuntimeError("No video generated by SadTalker")
            
        except Exception as e:
            logger.error(f"Error with SadTalker: {str(e)}")
            # Fallback to basic animation
            return self.create_basic_talking_video(image_path, audio_path, output_path)
    
    def create_basic_talking_video(self, image_path: str, audio_path: str, output_path: str) -> str:
        """Create basic talking video as fallback"""
        try:
            # Load the image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Get audio duration
            audio = AudioSegment.from_file(audio_path)
            duration_seconds = len(audio) / 1000.0
            
            # Video parameters
            fps = 30
            total_frames = int(duration_seconds * fps)
            height, width = img.shape[:2]
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Generate frames with enhanced mouth animation
            for frame_num in range(total_frames):
                current_frame = img.copy()
                
                # More sophisticated mouth animation
                time_factor = frame_num / fps
                mouth_open_factor = abs(np.sin(time_factor * 8)) * 0.6 + 0.2
                
                # Detect face area for mouth animation
                mouth_center = (width // 2, int(height * 0.7))
                mouth_width = int(30 * (1 + mouth_open_factor))
                mouth_height = int(12 * (1 + mouth_open_factor * 1.5))
                
                # Draw animated mouth
                cv2.ellipse(current_frame, mouth_center, (mouth_width, mouth_height), 
                           0, 0, 360, (120, 60, 60), -1)
                
                # Add subtle head movement
                shift_x = int(3 * np.sin(time_factor * 2))
                shift_y = int(2 * np.cos(time_factor * 1.5))
                
                # Apply movement
                M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
                current_frame = cv2.warpAffine(current_frame, M, (width, height))
                
                video_writer.write(current_frame)
            
            video_writer.release()
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating basic talking video: {str(e)}")
            raise
    
    def combine_video_with_backgrounds(self, avatar_video_path: str, audio_path: str, 
                                     script_segments: List[Dict], output_path: str) -> str:
        """Combine avatar video with changing backgrounds"""
        try:
            # For now, we'll use a simple approach
            # In a full implementation, this would composite the avatar over different backgrounds
            
            # Just return the avatar video for now
            # TODO: Implement background compositing
            
            # Combine with audio
            final_output = output_path.replace('.mp4', '_final.mp4')
            cmd = [
                'ffmpeg', '-y',
                '-i', avatar_video_path,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',
                final_output
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise RuntimeError(f"FFmpeg failed: {result.stderr}")
            
            return final_output
            
        except Exception as e:
            logger.error(f"Error combining video with backgrounds: {str(e)}")
            raise
    
    def generate_enhanced_avatar_video(self, audio_base64: str, avatar_option: str = "default",
                                     user_image_base64: str = None, script_text: str = "") -> Dict[str, Any]:
        """Main method to generate enhanced avatar video"""
        try:
            request_id = str(uuid.uuid4())[:8]
            logger.info(f"Starting enhanced avatar video generation (ID: {request_id})")
            
            # Convert audio from base64
            temp_audio_path = str(self.temp_dir / f"audio_{request_id}.mp3")
            wav_audio_path = self.audio_base64_to_file(audio_base64, temp_audio_path)
            
            # Determine avatar image
            if avatar_option == "upload" and user_image_base64:
                avatar_image_path = self.save_user_image(user_image_base64, request_id)
            elif avatar_option == "ai_generated":
                avatar_image_path = self.generate_ai_avatar_image("professional person")
            else:
                avatar_image_path = str(self.assets_dir / "default-avatar.jpg")
            
            # Parse script for background generation
            script_segments = self.parse_script_for_backgrounds(script_text)
            
            # Generate talking video
            temp_video_path = str(self.temp_dir / f"avatar_{request_id}.mp4")
            
            if self.sadtalker_available:
                avatar_video_path = self.create_talking_video_with_sadtalker(
                    avatar_image_path, wav_audio_path, temp_video_path
                )
            else:
                avatar_video_path = self.create_basic_talking_video(
                    avatar_image_path, wav_audio_path, temp_video_path
                )
            
            # Combine with backgrounds
            final_video_path = self.combine_video_with_backgrounds(
                avatar_video_path, wav_audio_path, script_segments, 
                str(self.temp_dir / f"final_{request_id}.mp4")
            )
            
            # Get video duration
            duration_seconds = self.get_video_duration(final_video_path)
            
            # Convert to base64
            with open(final_video_path, 'rb') as video_file:
                video_base64 = base64.b64encode(video_file.read()).decode('utf-8')
            
            # Cleanup
            cleanup_files = [temp_audio_path, wav_audio_path, temp_video_path, 
                           avatar_video_path, final_video_path]
            if avatar_option == "upload" or avatar_option == "ai_generated":
                cleanup_files.append(avatar_image_path)
            
            self.cleanup_temp_files(cleanup_files)
            
            return {
                "video_base64": video_base64,
                "duration_seconds": duration_seconds,
                "request_id": request_id,
                "avatar_option": avatar_option,
                "script_segments": len(script_segments),
                "sadtalker_used": self.sadtalker_available
            }
            
        except Exception as e:
            logger.error(f"Error generating enhanced avatar video: {str(e)}")
            raise
    
    def save_user_image(self, image_base64: str, request_id: str) -> str:
        """Save user uploaded image"""
        try:
            image_data = base64.b64decode(image_base64)
            image_path = str(self.temp_dir / f"user_avatar_{request_id}.jpg")
            
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            return image_path
            
        except Exception as e:
            logger.error(f"Error saving user image: {str(e)}")
            raise
    
    def audio_base64_to_file(self, audio_base64: str, output_path: str) -> str:
        """Convert base64 audio to file"""
        try:
            audio_data = base64.b64decode(audio_base64)
            
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            # Convert to WAV for better compatibility
            wav_path = output_path.replace('.mp3', '.wav').replace('.m4a', '.wav')
            audio = AudioSegment.from_file(output_path)
            audio.export(wav_path, format="wav")
            
            return wav_path
            
        except Exception as e:
            logger.error(f"Error converting audio: {str(e)}")
            raise
    
    def get_video_duration(self, video_path: str) -> float:
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
    
    def cleanup_temp_files(self, file_paths: List[str]):
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not cleanup file {file_path}: {str(e)}")

# Global instance
enhanced_avatar_generator = EnhancedAvatarGenerator()