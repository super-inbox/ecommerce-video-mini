"""
Text-to-Speech generator using Microsoft Azure Cognitive Services
"""

import azure.cognitiveservices.speech as speechsdk
from pathlib import Path
from typing import Optional


class TTSGenerator:
    """Generates audio narration using Azure TTS"""
    
    def __init__(self, subscription_key: str, region: str):
        """
        Initialize Azure TTS client
        
        Args:
            subscription_key: Azure Speech Services API key
            region: Azure region (e.g., 'eastus', 'westus')
        """
        self.speech_config = speechsdk.SpeechConfig(
            subscription=subscription_key,
            region=region
        )
        
        # Set voice - using a professional sounding voice
        # Available voices: https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support
        self.speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
        
        # Set output format to high quality
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )
    
    def generate_speech(
        self,
        text: str,
        output_file: str,
        voice_name: Optional[str] = None
    ) -> str:
        """
        Generate speech from text and save to file
        
        Args:
            text: Text to convert to speech
            output_file: Output audio file path
            voice_name: Optional voice name to override default
            
        Returns:
            Path to the generated audio file
        """
        try:
            # Override voice if specified
            if voice_name:
                self.speech_config.speech_synthesis_voice_name = voice_name
            
            # Create audio config for file output
            audio_config = speechsdk.audio.AudioOutputConfig(
                filename=output_file
            )
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Generate speech
            result = synthesizer.speak_text_async(text).get()
            
            # Check result
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"  ✓ Audio generated: {output_file}")
                return output_file
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                raise Exception(f"Speech synthesis canceled: {cancellation.reason}")
            else:
                raise Exception(f"Speech synthesis failed: {result.reason}")
                
        except Exception as e:
            raise Exception(f"Failed to generate speech: {str(e)}")
    
    def generate_speech_with_ssml(
        self,
        ssml: str,
        output_file: str
    ) -> str:
        """
        Generate speech using SSML for advanced control
        
        Args:
            ssml: SSML markup text
            output_file: Output audio file path
            
        Returns:
            Path to the generated audio file
        """
        try:
            audio_config = speechsdk.audio.AudioOutputConfig(
                filename=output_file
            )
            
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return output_file
            else:
                raise Exception(f"SSML synthesis failed: {result.reason}")
                
        except Exception as e:
            raise Exception(f"Failed to generate speech with SSML: {str(e)}")
    
    def create_ssml(
        self,
        text: str,
        voice: str = "en-US-JennyNeural",
        rate: str = "0%",
        pitch: str = "0%"
    ) -> str:
        """
        Create SSML markup for advanced speech control
        
        Args:
            text: Text content
            voice: Voice name
            rate: Speech rate (-50% to +50%)
            pitch: Pitch adjustment (-50% to +50%)
            
        Returns:
            SSML string
        """
        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
            <voice name='{voice}'>
                <prosody rate='{rate}' pitch='{pitch}'>
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        return ssml.strip()
    
    @staticmethod
    def get_available_voices() -> dict:
        """
        Get dictionary of recommended voices for different styles
        
        Returns:
            Dictionary of voice names by style
        """
        return {
            'professional_female': 'en-US-JennyNeural',
            'professional_male': 'en-US-GuyNeural',
            'warm_female': 'en-US-AriaNeural',
            'friendly_male': 'en-US-DavisNeural',
            'energetic_female': 'en-US-SaraNeural',
            'authoritative_male': 'en-US-TonyNeural'
        }