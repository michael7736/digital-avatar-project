# 数字人直播系统

一个高度模块化的数字人直播系统，支持语音合成与克隆、虚拟形象创作与渲染、实时动画与唇语同步、对话管理以及直播流集成。

## 功能模块

系统包含以下主要模块：

1. **语音合成与克隆**：将文本转换为语音，支持多种声音风格和情感，以及克隆指定声音。
2. **虚拟形象创作与渲染**：创建和渲染3D虚拟形象。
3. **实时动画与唇语同步**：基于生成的语音实现逼真的唇语同步和面部动画。
4. **对话管理(Chatbot)**：处理用户输入，生成回复，管理对话状态。
5. **直播流集成**：将生成的音视频内容整合并输出到直播平台。

## 项目结构

```
digital_avatar_project/
├── modules/
│   ├── voice_synthesis/     # 语音合成与克隆模块
│   ├── face_animation/      # 虚拟形象创作与渲染模块
│   ├── lip_sync/            # 实时动画与唇语同步模块
│   ├── chatbot/             # 对话管理模块
│   ├── streaming/           # 直播流集成模块
│   └── utils/               # 工具函数
├── configs/                 # 配置文件
├── main.py                  # 主程序入口
├── README.md                # 项目说明
└── requirements.txt         # 项目依赖
```

## 安装和使用

1. 克隆项目：
```bash
git clone https://github.com/yourusername/digital_avatar_project.git
cd digital_avatar_project
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 设置配置：
- 在`configs/default.json`中配置各模块参数
- OpenAI API密钥可以设置环境变量：`export OPENAI_API_KEY=your_api_key`

4. 运行测试脚本：
```bash
python test.py
```

5. 运行完整系统：
```bash
python main.py
```

6. 高级参数：
```bash
python main.py --config configs/custom.json --debug --no-stream
```

## 模块定制

该系统采用高度模块化设计，可以轻松替换各个组件：

### 语音合成

支持以下引擎：
- OpenAI TTS
- Azure TTS
- Edge TTS
- 自定义TTS引擎

配置示例：
```json
"voice_synthesis": {
    "engine": "openai",
    "voice": "alloy",
    "language": "zh-CN",
    "pitch": 1.0,
    "rate": 1.0
}
```

### 虚拟形象

支持以下模型类型：
- 2D图像
- 3D模型（实验性）

配置示例：
```json
"face_animation": {
    "model": "2d",
    "avatar_path": "assets/avatars/custom.png",
    "animations_enabled": true
}
```

### 唇语同步

支持以下引擎：
- Wav2Lip
- SadTalker
- 自定义引擎

配置示例：
```json
"lip_sync": {
    "engine": "sad_talker",
    "preprocess": "full",
    "enhancer": "gfpgan",
    "frame_rate": 30
}
```

### 对话管理

支持以下引擎：
- OpenAI Chat API
- LangChain
- 自定义对话引擎

配置示例：
```json
"chatbot": {
    "engine": "openai",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_history": 10,
    "system_prompt": "你是一个友好的数字人助手。"
}
```

### 直播推流

支持以下平台：
- RTMP（推流到直播服务器）
- 虚拟摄像头

配置示例：
```json
"streaming": {
    "platform": "rtmp",
    "url": "rtmp://localhost/live",
    "key": "stream",
    "resolution": "720p"
}
```

## 依赖技术

- 语音合成：OpenAI TTS, Azure TTS, Edge TTS
- 唇语同步：Wav2Lip, SadTalker
- 虚拟形象：基于OpenCV和自定义3D渲染
- 对话管理：OpenAI GPT, LangChain
- 直播流：FFmpeg, RTMP

## 注意事项

- 首次运行时会创建默认配置和资源
- 某些功能需要下载预训练模型
- 推流功能需要配置好RTMP服务器 