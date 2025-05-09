# Digital Human Live System

A highly modular digital human live streaming system supporting voice synthesis, avatar rendering, lip sync, dialogue management, and streaming integration.

## Features

- **Highly Modular**: All components can be independently replaced and customized
- **Multi-Engine Support**: Multiple voice synthesis, lip sync, and dialogue management engines
- **Configurable**: Easily customize system behavior through JSON configuration files
- **Real-time Performance**: Optimized rendering and synchronization algorithms for smooth streaming
- **Cross-Platform**: Support for Windows, macOS, and Linux platforms

## System Modules

### 1. Voice Synthesis and Cloning

Support for multiple voice synthesis engines:
- OpenAI TTS
- Azure TTS
- Edge TTS
- Local voice cloning models

### 2. Avatar Creation and Rendering

Support for multiple avatar types:
- 2D avatars (PNG sequences/Live2D)
- 3D models (VRM/FBX)
- Real-time rendering (OpenGL/DirectX)

### 3. Real-time Animation and Lip Sync

Support for multiple lip sync technologies:
- Wav2Lip
- SadTalker
- Phoneme-based lip matching

### 4. Dialogue Management System

Support for multiple dialogue engines:
- OpenAI API
- LangChain
- Local LLM models
- Custom dialogue logic

### 5. Streaming Integration

Support for multiple streaming output methods:
- RTMP push (OBS/Bilibili/YouTube, etc.)
- Virtual camera output
- Local video saving

## Quick Start

### Requirements

- Python 3.8+
- CUDA-compatible GPU (for acceleration of certain modules)
- FFmpeg

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/digital_human_live.git
cd digital_human_live

# Install dependencies
pip install -r requirements.txt

# Install optional dependencies (as needed)
pip install -r requirements_optional.txt
```

### Configuration

1. Copy the default configuration file
```bash
cp configs/default.json configs/my_config.json
```

2. Edit the configuration file to set your API keys and module parameters

### Run

```bash
python main.py --config configs/my_config.json
```

## Custom Modules

The system design allows for easy replacement of any module:

1. Create a new class that implements the corresponding interface
2. Specify your custom module in the configuration file
3. The system will automatically load your implementation

## License

MIT License

## Contributing

Contributions via Pull Requests or Issues are welcome! Please refer to the [Contributing Guidelines](CONTRIBUTING.md) for more information. 