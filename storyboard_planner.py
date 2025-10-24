"""
Storyboard planner using GPT-4o-mini to create video scenes
"""

import json
from typing import Dict, List
from openai import OpenAI


class StoryboardPlanner:
    """Uses GPT-4o-mini to plan video storyboard"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
    
    def create_storyboard(
        self,
        images: List[Dict],
        descriptions: List[str],
        brand_name: str,
        target_duration: int = 30
    ) -> Dict:
        """
        Create a storyboard with 4-6 scenes
        
        Args:
            images: List of image dictionaries with paths and metadata
            descriptions: List of text descriptions from the website
            brand_name: Name of the brand/company
            target_duration: Target video duration in seconds
            
        Returns:
            Storyboard dictionary with scenes
        """
        
        # Prepare context for GPT
        image_info = [
            f"Image {i+1}: {img.get('alt', 'No description')} (path: {img['local_path']})"
            for i, img in enumerate(images[:15])  # Limit to 15 for context
        ]
        
        descriptions_text = "\n".join([f"- {desc[:200]}" for desc in descriptions[:8]])
        
        prompt = f"""You are a professional video marketing specialist. Create a compelling 30-second video storyboard for {brand_name}.

Available images:
{chr(10).join(image_info)}

Product/Brand descriptions:
{descriptions_text}

Create a storyboard with 4-6 scenes (ideal for a 30-second video). Each scene should:
1. Use one of the available images (reference by image number)
2. Have engaging narration text (10-20 words that can be spoken in 4-6 seconds)
3. Have a suggested duration (4-6 seconds per scene)

The FINAL scene MUST be a closing scene with a memorable tagline about {brand_name}.

Return a JSON object with this structure:
{{
  "scenes": [
    {{
      "scene_number": 1,
      "image_index": 0,
      "narration": "Compelling narration text here",
      "duration": 5,
      "purpose": "Brief description of scene purpose"
    }}
  ],
  "tagline": "Final memorable tagline",
  "total_duration": 30
}}

Make the narration conversational, engaging, and perfect for voice-over. The final scene should have a strong call-to-action or brand message."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional video marketing specialist who creates engaging storyboards. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            storyboard_data = json.loads(response.choices[0].message.content)
            
            # Map image indices to actual image paths
            for scene in storyboard_data['scenes']:
                img_idx = scene['image_index']
                if img_idx < len(images):
                    scene['image_path'] = images[img_idx]['local_path']
                    scene['image_url'] = images[img_idx]['url']
                else:
                    # Fallback to first image if index out of range
                    scene['image_path'] = images[0]['local_path']
                    scene['image_url'] = images[0]['url']
            
            storyboard_data['brand_name'] = brand_name
            
            return storyboard_data
            
        except Exception as e:
            raise Exception(f"Failed to create storyboard: {str(e)}")
    
    def optimize_scene_timing(self, storyboard: Dict, total_duration: int = 30) -> Dict:
        """
        Optimize scene durations to fit target total duration
        
        Args:
            storyboard: Storyboard dictionary
            total_duration: Target total duration in seconds
            
        Returns:
            Updated storyboard with adjusted timings
        """
        scenes = storyboard['scenes']
        current_total = sum(scene['duration'] for scene in scenes)
        
        if current_total != total_duration:
            # Scale durations proportionally
            scale_factor = total_duration / current_total
            for scene in scenes:
                scene['duration'] = round(scene['duration'] * scale_factor, 1)
        
        storyboard['total_duration'] = sum(scene['duration'] for scene in scenes)
        return storyboard