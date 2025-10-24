# Website to Video Generator

Automatically generate 30-second marketing videos from website content using AI-powered storyboarding and text-to-speech.

## Features

- 🌐 **Website Scraping**: Extracts images and product descriptions from any URL
- 🎬 **AI Storyboarding**: Uses GPT-4o-mini to create compelling 4-6 scene storyboards
- 🎙️ **Professional Narration**: Generates voice-over using Microsoft Azure TTS
- 🎥 **Video Composition**: Automatically stitches everything into a polished video

## Requirements

- Python 3.8+
- FFmpeg (for video processing)
- OpenAI API key (for GPT-4o-mini)
- Microsoft Azure Speech Services API key

## Installation

### 1. Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

### 2. Clone and Setup

```bash
git clone <repository-url>
cd website-video-generator
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `AZURE_TTS_KEY`: Your Azure Speech Services key
- `AZURE_TTS_REGION`: Azure region (e.g., `eastus`, `westus2`)

## Usage

### Basic Usage

```bash
python main.py https://example.com
```

### Specify Output File

```bash
python main.py https://example.com my_video.mp4
```

### Programmatic Usage

```python
from config import Config
from main import VideoGenerator

# Configure
config = Config(
    openai_api_key="your_key",
    azure_tts_key="your_key",
    azure_tts_region="eastus"
)

# Generate video
generator = VideoGenerator(config)
result = generator.generate_video(
    url="https://example.com",
    output_path="output.mp4"
)

if result['success']:
    print(f"Video created: {result['video_path']}")
```

## Project Structure

```
.
├── main.py                 # Main entry point
├── config.py              # Configuration management
├── scraper.py             # Website scraper
├── storyboard_planner.py  # AI-powered storyboard creation
├── tts_generator.py       # Azure TTS integration
├── video_composer.py      # Video assembly
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## How It Works

1. **Scraping**: The scraper downloads images and extracts text content from the target website
2. **Planning**: GPT-4o-mini analyzes the content and creates a 4-6 scene storyboard with narration
3. **Narration**: Azure TTS generates professional voice-over for each scene
4. **Composition**: MoviePy stitches images and audio into a final video with transitions

## API Keys Setup

### OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Create an account or sign in
3. Navigate to API keys section
4. Create a new API key
5. Add to your `.env` file

### Azure Speech Services

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a "Speech Services" resource
3. Copy the key and region
4. Add to your `.env` file

## Customization

### Change Voice Style

Edit `tts_generator.py`:

```python
# Available voices
self.speech_config.speech_synthesis_voice_name = "en-US-GuyNeural"  # Male voice
# or
self.speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"  # Warm female
```

### Adjust Video Settings

Edit `.env`:

```bash
TARGET_DURATION=45  # Change video length
MIN_SCENES=5        # Minimum number of scenes
MAX_SCENES=8        # Maximum number of scenes
```

### Video Resolution

Edit `main.py`:

```python
self.composer = VideoComposer(
    fps=30,                    # Frame rate
    resolution=(1920, 1080)    # Resolution
)
```

## Troubleshooting

### FFmpeg Not Found

Ensure FFmpeg is installed and in your PATH:

```bash
ffmpeg -version
```

### Azure TTS Errors

- Verify your API key and region are correct
- Check your Azure subscription has available quota
- Ensure you're using a valid region (e.g., `eastus`, `westus2`)

### OpenAI API Errors

- Verify your API key is active
- Check you have sufficient credits
- Ensure you have access to GPT-4o-mini model

### Memory Issues

For large videos, you may need to:
- Reduce image resolution
- Limit number of images
- Increase system swap space

## License

MIT License - feel free to use for commercial projects

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For issues and questions:
- Open a GitHub issue
- Check Azure TTS documentation: [docs.microsoft.com/azure/cognitive-services/speech-service](https://docs.microsoft.com/azure/cognitive-services/speech-service)
- Check OpenAI documentation: [platform.openai.com/docs](https://platform.openai.com/docs)
