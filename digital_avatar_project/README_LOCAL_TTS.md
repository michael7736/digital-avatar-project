# 本地TTS引擎使用指南

本文档介绍如何在数字人项目中设置和使用开源本地部署的TTS（文本转语音）引擎。这种方案无需联网，可以完全在本地运行，适合保护隐私和离线应用场景。

## 特点

- 完全本地部署，无需联网
- 开源免费，不需要API密钥
- 支持多种语言（包括优质中文）
- 可训练自定义声音模型
- 集成简单，易于使用

## 安装依赖

首先，你需要安装Coqui TTS包及其依赖：

```bash
# 安装基本依赖
pip install TTS

# 可选：安装GPU加速支持（推荐，需要CUDA环境）
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# 可选：安装音频播放工具（用于演示）
pip install playsound
```

## 配置说明

在`config`目录下有一个示例配置文件`tts_config_local.yaml`，你可以根据需要修改：

```yaml
# 基本配置
engine: coqui  # 使用开源的Coqui TTS引擎
output_dir: "temp/audio"  # 音频输出目录

# Coqui TTS配置
## 方式1: 使用预训练模型（推荐简单入门）
model_name: "tts_models/zh-CN/baker/tacotron2-DDC-GST"  # 中文预训练模型
use_cuda: true  # 是否使用GPU加速（推荐启用）

## 方式2: 使用本地自定义模型（适合高级自定义）
# model_path: "path/to/your/model.pth"  # 模型路径
# config_path: "path/to/your/config.json"  # 配置文件路径
# vocoder_path: "path/to/your/vocoder.pth"  # 声码器路径（可选）
# vocoder_config_path: "path/to/your/vocoder_config.json"  # 声码器配置文件路径（可选）

# 合成选项
# speaker: "your_speaker_name"  # 多说话人模型的说话人名称（可选）
# language: "zh-cn"  # 多语言模型的语言代码（可选）
```

## 预训练模型推荐

Coqui TTS提供了多种预训练模型，首次运行时会自动下载。以下是一些推荐：

### 中文模型
- `tts_models/zh-CN/baker/tacotron2-DDC-GST`：高质量中文女声（推荐）
- `tts_models/multilingual/multi-dataset/your_tts`：多语言支持，包含中文

### 英文模型
- `tts_models/en/ljspeech/tacotron2-DDC`：经典英文女声
- `tts_models/en/ljspeech/glow-tts`：快速合成英文女声
- `tts_models/en/ljspeech/vits`：高质量英文女声

## 使用方法

### 运行示例

我们提供了一个简单的示例脚本，你可以直接运行它来测试本地TTS引擎：

```bash
cd digital_avatar_project
python examples/local_tts_demo.py
```

### 在代码中使用

```python
from modules.voice_synthesis.tts_manager import TTSManager

# 加载配置
config = {
    "engine": "coqui",
    "model_name": "tts_models/zh-CN/baker/tacotron2-DDC-GST",
    "use_cuda": True,
    "output_dir": "temp/audio"
}

# 初始化TTS管理器
tts_manager = TTSManager(config)

# 合成语音
audio_path = tts_manager.synthesize("你好，这是一段测试语音。")
print(f"音频保存路径: {audio_path}")
```

## 训练自定义声音

如果你想使用自己的声音或其他声音，可以训练自定义模型。这需要一些语音数据和训练过程。

### 准备数据
1. 准备10-30分钟高质量朗读录音（越多越好）
2. 文本和音频对齐标注
3. 数据集格式化（详见Coqui TTS文档）

### 训练模型
参考Coqui TTS的训练文档：https://tts.readthedocs.io/en/latest/training_a_model.html

训练完成后，修改配置文件使用本地模型：

```yaml
engine: coqui
model_path: "path/to/your/model.pth"
config_path: "path/to/your/config.json"
```

## 常见问题

### Q: 首次运行很慢
A: 首次运行需要下载预训练模型，请保持网络连接并耐心等待。下载后的模型会缓存在本地。

### Q: 语音质量不理想
A: 尝试使用不同的预训练模型，或调整合成参数。VITS和YourTTS通常有较好的质量。

### Q: 显存不足错误
A: 设置`use_cuda: false`禁用GPU加速，或尝试使用更小的模型。

### Q: 支持哪些音频格式
A: 默认输出为WAV格式，可以使用其他工具转换为MP3等格式。

## 其他开源TTS选项

除了Coqui TTS外，还有其他开源TTS选项：

1. **Mozilla TTS**：Coqui TTS的前身
2. **ESPnet-TTS**：功能强大的语音处理工具箱
3. **FastSpeech2**：快速并行TTS模型实现
4. **VITS**：端到端高质量TTS模型

如需集成其他TTS引擎，请参考`TTSManager`类中的自定义TTS实现。 