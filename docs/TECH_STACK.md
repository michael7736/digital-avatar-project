# Tech Stack Definition

## 1. Project Overview & Goals
本项目为AI驱动的虚拟数字人直播系统，目标是降低直播门槛、提升内容创作效率、丰富互动形式，实现"无人直播"或辅助真人主播，支持7×24小时内容输出。技术目标包括：高可用、易扩展、支持多平台推流、AI能力本地化、开发效率优先。

## 2. Core Languages & Runtimes
- 后端：Python 3.10+（因AI生态丰富、异步支持好、团队熟悉）
- 前端：TypeScript + React（推荐）或 Vue（可选），支持现代Web开发和高效组件化
- 运行环境：Node.js（前端构建）、Python 3.10+（后端/AI服务）

## 3. Frameworks & Libraries (Backend)
- FastAPI（主后端框架，异步高性能，API友好）
- SQLAlchemy（ORM）
- Celery（任务调度/异步任务）
- Coqui TTS（本地TTS服务）
- Wav2Lip/MuseTalk（唇形同步）
- OpenAI/Claude API（LLM对接，可选）
- Pydantic（数据校验）

## 4. Frameworks & Libraries (Frontend)
- React 18+（推荐）或 Vue 3
- Three.js（3D渲染，二期）
- Live2D/Spine（2D数字人渲染）
- Ant Design/Tailwind CSS（UI组件库/样式）
- Zustand/Redux（状态管理）
- WebSocket（实时互动）

## 5. Database & Data Storage
- 主数据库：PostgreSQL（生产环境）、SQLite（开发/测试）
- FAQ/检索：Elasticsearch/Faiss（可选，提升FAQ检索效率）
- 缓存：Redis（会话、任务队列等）
- 对象存储：本地文件系统或S3兼容存储（直播回放、素材）

## 6. Infrastructure & Deployment
- 容器化：Docker、Docker Compose
- 部署环境：本地服务器或云主机（如阿里云、腾讯云、AWS均可）
- 反向代理：Nginx
- CI/CD：GitHub Actions（推荐）、GitLab CI
- 负载均衡/扩展：Kubernetes（后期可选）

## 7. APIs & Integrations
- 自有API：RESTful（主）、WebSocket（直播互动）
- 第三方集成：
  - OBS Studio（虚拟摄像头/推流）
  - OpenAI/Claude（LLM问答）
  - 直播平台弹幕/评论接口（如抖音、快手，需适配）
  - 邮件/短信服务（如SendGrid、Twilio，可选）

## 8. Development Tools & Standards
- 版本控制：Git，代码托管于GitHub
- 代码规范：Black（Python）、Prettier/ESLint（前端）
- IDE：VSCode（推荐）
- 测试：PyTest（后端单元/集成）、Jest/React Testing Library（前端）、Cypress（E2E）
- 文档：OpenAPI（API文档）、Storybook（前端组件）

## 9. Security Considerations
- 身份认证：JWT/OAuth2
- 输入校验与防注入：Pydantic、ORM参数化
- HTTPS加密、敏感信息加密存储
- 依赖漏洞扫描：Dependabot、pip-audit
- 内容安全：敏感词过滤、AI内容审核
- 日志与审计：操作日志、异常监控

## 10. Rationale & Alternatives Considered
- Python+FastAPI选型因AI生态和异步性能优越，Django未选因偏重传统Web。
- React优先于Vue因团队经验和生态，Vue可选。
- PostgreSQL因关系型数据和扩展性，MongoDB未选因结构化需求为主。
- OBS Studio为推流事实标准，FFmpeg为底层推流备选。
- LLM优先用API，后期可本地化。
- 容器化为主流部署方式，K8s为后期扩展预留。 