"""
Configuration management for the video generator
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration for video generator"""
    
    openai_api_key: str
    azure_tts_key: str
    azure_tts_region: str
    target_duration: int = 30  # Target video duration in seconds
    scenes_count_range: tuple = (4, 6)  # Min and max number of scenes
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        
        openai_key = os.getenv('OPENAI_API_KEY')
        azure_key = os.getenv('AZURE_TTS_KEY')
        azure_region = os.getenv('AZURE_TTS_REGION')
        
        if not openai_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        if not azure_key:
            raise ValueError("AZURE_TTS_KEY environment variable not set")
        if not azure_region:
            raise ValueError("AZURE_TTS_REGION environment variable not set")
        
        return cls(
            openai_api_key=openai_key,
            azure_tts_key=azure_key,
            azure_tts_region=azure_region,
            target_duration=int(os.getenv('TARGET_DURATION', '30')),
            scenes_count_range=(
                int(os.getenv('MIN_SCENES', '4')),
                int(os.getenv('MAX_SCENES', '6'))
            )
        )
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'Config':
        """Create config from dictionary"""
        return cls(
            openai_api_key=config_dict['openai_api_key'],
            azure_tts_key=config_dict['azure_tts_key'],
            azure_tts_region=config_dict['azure_tts_region'],
            target_duration=config_dict.get('target_duration', 30),
            scenes_count_range=tuple(config_dict.get('scenes_count_range', [4, 6]))
        )