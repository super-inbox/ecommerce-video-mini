"""
Website to Video Generator
Main entry point for the application
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any
import json

from scraper import WebsiteScraper
from storyboard_planner import StoryboardPlanner
from tts_generator import TTSGenerator
from video_composer import VideoComposer
from config import Config


class VideoGenerator:
    """Main orchestrator for the video generation pipeline"""
    
    def __init__(self, config: Config):
        self.config = config
        self.scraper = WebsiteScraper()
        self.planner = StoryboardPlanner(config.openai_api_key)
        self.tts = TTSGenerator(config.azure_tts_key, config.azure_tts_region)
        self.composer = VideoComposer()
        
    def generate_video(self, url: str, output_path: str = "output_video.mp4") -> Dict[str, Any]:
        """
        Generate a video from a website URL
        
        Args:
            url: Website URL to scrape
            output_path: Path for the output video file
            
        Returns:
            Dictionary with generation results and metadata
        """
        try:
            print(f"Step 1: Scraping website: {url}")
            scraped_data = self.scraper.scrape(url)
            print(f"  - Found {len(scraped_data['images'])} images")
            print(f"  - Extracted product descriptions")
            
            print("\nStep 2: Planning storyboard with GPT-4o-mini")
            storyboard = self.planner.create_storyboard(
                images=scraped_data['images'],
                descriptions=scraped_data['descriptions'],
                brand_name=scraped_data['brand_name']
            )
            print(f"  - Created {len(storyboard['scenes'])} scenes")
            
            print("\nStep 3: Generating narration with Azure TTS")
            audio_files = []
            for i, scene in enumerate(storyboard['scenes']):
                print(f"  - Generating audio for scene {i+1}")
                audio_path = self.tts.generate_speech(
                    text=scene['narration'],
                    output_file=f"temp_audio_scene_{i+1}.mp3"
                )
                audio_files.append(audio_path)
                scene['audio_file'] = audio_path
            
            print("\nStep 4: Composing video")
            video_path = self.composer.create_video(
                storyboard=storyboard,
                output_path=output_path
            )
            print(f"  - Video saved to: {video_path}")
            
            # Cleanup temp files
            self._cleanup_temp_files(audio_files)
            
            return {
                "success": True,
                "video_path": video_path,
                "storyboard": storyboard,
                "metadata": {
                    "url": url,
                    "scenes": len(storyboard['scenes']),
                    "duration": storyboard.get('total_duration', 30)
                }
            }
            
        except Exception as e:
            print(f"Error generating video: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _cleanup_temp_files(self, files: list):
        """Clean up temporary audio files"""
        for file in files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                print(f"Warning: Could not delete temp file {file}: {e}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python main.py <website_url> [output_file]")
        sys.exit(1)
    
    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output_video.mp4"
    
    # Load configuration
    config = Config.from_env()
    
    # Generate video
    generator = VideoGenerator(config)
    result = generator.generate_video(url, output_file)
    
    if result['success']:
        print("\n✓ Video generation complete!")
        print(f"Video saved to: {result['video_path']}")
    else:
        print(f"\n✗ Video generation failed: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()