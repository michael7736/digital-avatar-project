# 技术方案说明（TECHSPEC）

## 1. 总体架构
系统采用模块化设计，分为前端、后端、AI服务、推流服务和数据管理五大核心部分。整体架构如下：

- **前端**：Web端（React/Vue），负责用户交互、数字人渲染、直播场景配置、内容编辑等。
- **后端**：Python（FastAPI/Flask），负责业务逻辑、用户管理、内容管理、AI服务编排、推流控制。
- **AI服务**：包括TTS（F5 TTS，Docker部署）、唇形同步（Wav2Lip/MuseTalk）、NLP（FAQ检索+LLM）、ASR（Faster-Whisper，Docker部署）。
- **推流服务**：集成OBS虚拟摄像头和RTMP推流，支持多平台分发。
- **数据管理**：数据库（PostgreSQL/SQLite），存储用户、数字人、脚本、FAQ、直播日志等。

## 2. 关键技术选型
- **前端**：React（推荐）或Vue，Three.js（3D）、Live2D/Spine（2D）、WebSocket（实时交互）。
- **后端**：Python 3.10+，FastAPI（推荐，异步高性能）、SQLAlchemy、Celery（任务调度）。
- **AI语音合成**：F5 TTS（Docker部署，支持多音色、多语言）。
- **唇形同步**：Wav2Lip（2D）、MuseTalk（3D/2D）、自研动画映射。
- **NLP/对话**：RAG（FAQ检索）、OpenAI/Claude API（LLM）、自定义Prompt。
- **ASR**：Faster-Whisper（Docker部署，支持高效语音识别）。
- **推流**：OBS Studio（虚拟摄像头）、FFmpeg（RTMP）、OBS多平台插件。
- **数据库**：PostgreSQL（生产）、SQLite（开发/测试）。
- **部署**：Docker Compose（推荐）、本地/云服务器均可。

## 3. 模块划分与接口设计
### 3.1 前端模块
- 用户登录/注册、数字人管理、内容脚本编辑、直播场景配置、直播控制台、数据统计。
- 2D数字人渲染（Live2D/Spine）、3D数字人渲染（Three.js，二期）。
- WebSocket用于直播互动、状态同步。

### 3.2 后端模块
- 用户与权限管理
- 数字人形象与声音管理
- 内容脚本与FAQ管理
- AI服务编排（TTS、唇形同步、NLP、ASR）
- 推流控制与日志
- 数据统计与内容审核

#### 主要接口（RESTful+WebSocket）
- /api/login, /api/register
- /api/avatar (GET/POST/PUT/DELETE)
- /api/script (GET/POST/PUT/DELETE)
- /api/faq (GET/POST/PUT/DELETE)
- /api/scene (GET/POST/PUT/DELETE)
- /api/stream/start, /api/stream/stop
- /ws/live (WebSocket互动)

### 3.3 AI服务模块
- TTS服务：F5 TTS（Docker），文本转语音，支持多音色、情感参数。
- 唇形同步服务：输入音频和人脸/动画参数，输出唇形动画帧。
- NLP服务：FAQ检索、LLM问答、弹幕意图识别。
- ASR服务：Faster-Whisper（Docker），语音弹幕转文本。

### 3.4 推流服务
- OBS虚拟摄像头：数字人画面作为摄像头信号输入平台官方直播工具。
- RTMP推流：FFmpeg/OBS将音视频流推送至目标平台。
- 多平台推流：OBS多平台插件或多路推流进程。

### 3.5 数据管理
- 用户表、数字人表、脚本表、FAQ表、直播日志表、内容审核表。
- 支持内容版本管理和回溯。

## 4. 数据流与处理流程
1. 用户在前端创建/编辑数字人、脚本、FAQ。
2. 启动直播后，后端调度AI服务：
   - 预录脚本：TTS（F5 TTS）生成语音，唇形同步生成动画帧，合成音视频流。
   - 互动问答：NLP解析弹幕，FAQ检索或LLM生成答案，TTS+唇形同步驱动数字人。
   - 语音弹幕：ASR（Faster-Whisper）转文本，进入NLP处理。
3. 推流服务将合成音视频流推送至OBS/RTMP。
4. 直播日志、互动数据实时写入数据库。

## 5. AI模型集成方案
- TTS：F5 TTS通过Docker部署，支持多音色/多语言，API接口封装。
- 唇形同步：Wav2Lip（2D）、MuseTalk（3D/2D），本地推理或微服务部署。
- NLP：FAQ检索（Elasticsearch/Faiss）、LLM（OpenAI/Claude API），可切换。
- ASR：Faster-Whisper通过Docker部署，API接口封装。

## 6. 推流与多平台分发
- OBS虚拟摄像头：推荐用于抖音、视频号等不开放推流码的平台。
- RTMP推流：用于快手、小红书等支持推流码的平台。
- 多平台同步：OBS多平台插件或多进程推流。

## 7. 部署方案
- 推荐Docker Compose一键部署，支持本地和云端。
- AI服务（F5 TTS、Faster-Whisper等）均以独立Docker容器部署，便于扩展和维护。
- 支持HTTPS、反向代理、负载均衡。

## 8. 开发计划（里程碑）
1. 项目初始化与基础架构搭建
2. 2D数字人形象与F5 TTS集成（Docker）
3. 内容脚本与FAQ管理模块开发
4. 直播场景与推流模块开发
5. 直播互动与NLP/LLM集成，Faster-Whisper（Docker）ASR集成
6. 唇形同步与动画驱动
7. 多平台推流与数据统计
8. 系统测试与优化，文档完善
9. 上线发布与用户反馈收集

---

如需详细接口文档、数据库ER图或微服务部署脚本，可后续补充。 