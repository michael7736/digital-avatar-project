# 数字人直播系统

一个高度模块化的数字人直播系统，支持语音合成、虚拟形象渲染、唇语同步、对话管理和直播流集成。

## 功能特点

- **高度模块化**: 所有组件都可以独立替换和定制
- **多引擎支持**: 支持多种语音合成、唇语同步、对话管理引擎
- **可配置**: 通过JSON配置文件轻松定制系统行为
- **实时性能**: 优化的渲染和同步算法确保直播流畅度
- **跨平台**: 支持Windows、macOS和Linux平台

## 系统模块

### 1. 语音合成与克隆 (Voice Synthesis)

支持多种语音合成引擎：
- OpenAI TTS
- Azure TTS
- Edge TTS
- 本地语音克隆模型

### 2. 虚拟形象创作与渲染 (Avatar Rendering)

支持多种虚拟形象类型：
- 2D形象（PNG序列/Live2D）
- 3D模型（VRM/FBX）
- 实时渲染（OpenGL/DirectX）

### 3. 实时动画与唇语同步 (Animation Sync)

支持多种唇语同步技术：
- Wav2Lip
- SadTalker
- 基于音素的唇形匹配

### 4. 对话管理系统 (Dialogue Management)

支持多种对话引擎：
- OpenAI API
- LangChain
- 本地LLM模型
- 自定义对话逻辑

### 5. 直播流集成 (Streaming Integration)

支持多种直播输出方式：
- RTMP推流（OBS/Bilibili/YouTube等）
- 虚拟摄像头输出
- 本地视频保存

## 快速开始

### 环境要求

- Python 3.8+
- CUDA支持的GPU（用于部分模块的加速）
- FFmpeg

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/digital_human_live.git
cd digital_human_live

# 安装依赖
pip install -r requirements.txt

# 安装可选依赖（根据需要）
pip install -r requirements_optional.txt
```

### 配置

1. 复制默认配置文件
```bash
cp configs/default.json configs/my_config.json
```

2. 编辑配置文件，设置您的API密钥和模块参数

### 运行

```bash
python main.py --config configs/my_config.json
```

## 自定义模块

系统设计允许轻松替换任何模块：

1. 创建一个实现相应接口的新类
2. 在配置文件中指定您的自定义模块
3. 系统将自动加载您的实现

## 许可证

MIT License

## 贡献指南

欢迎提交Pull Request或Issue！请参阅[贡献指南](CONTRIBUTING.md)了解更多信息。 