# 自动打轴工具

基于阿里云百练 funASR 的字幕自动对齐工具，支持上传音频和文案，自动识别并匹配时间轴，生成 SRT 字幕文件。

## 功能特点

- 🎵 支持多种音频格式（MP3、WAV、M4A、OGG 等）
- ✍️ 文案按行输入，自动匹配时间轴
- 🎬 实时预览字幕效果
- ✏️ 支持手动调整时间轴
- 📥 导出标准 SRT 字幕文件
- 🐳 Docker 一键部署

## 技术栈

- **前端**: Vue 3 + Element Plus
- **后端**: FastAPI (Python)
- **语音识别**: 阿里云百练 funASR
- **存储**: 服务器本地 + Nginx
- **部署**: Docker + Docker Compose

## 快速开始

### 1. 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 阿里云百炼 API Key

### 2. 获取 API Key

1. 登录 [阿里云百炼控制台](https://bailian.console.aliyun.com/)
2. 开通 FunASR 服务
3. 获取 API Key

### 3. 部署

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd zimu

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 API Key 和服务器地址

# 3. 构建并启动
docker-compose up -d --build

# 4. 访问
# 前端: http://你的服务器IP:3000
```

### 4. 使用流程

1. **上传音频**: 拖拽或点击上传音频文件
2. **输入文案**: 在文本框中输入字幕文案，每行一句
3. **开始识别**: 点击"开始识别与对齐"
4. **预览调整**: 预览字幕效果，拖拽调整时间轴
5. **导出 SRT**: 点击导出下载 SRT 文件

## 目录结构

```
zimu/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心模块
│   │   ├── models/      # 数据模型
│   │   └── utils/       # 工具函数
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             # 前端服务
│   ├── src/
│   │   ├── components/  # Vue 组件
│   │   ├── views/       # 页面视图
│   │   └── api/         # API 调用
│   ├── package.json
│   └── Dockerfile
├── data/                 # 数据目录
│   └── audio/           # 音频文件
├── docker-compose.yml
├── nginx.conf           # Nginx 配置
└── .env.example          # 环境变量示例
```

## 端口说明

| 端口 | 服务 | 说明 |
|------|------|------|
| 3000 | 前端 | Web 界面访问 |
| 8000 | 后端 | API 服务 |
| 8080 | Nginx | 音频文件访问 |

## API 接口

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/upload/audio` | 上传音频文件 |
| POST | `/api/asr/align` | 提交对齐任务 |
| GET | `/api/asr/status/{task_id}` | 查询任务状态 |
| POST | `/api/export/srt` | 导出 SRT 文件 |

详细 API 文档访问: `http://localhost:8000/docs`

## 本地开发

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 常见问题

### Q: 识别需要多长时间？
A: 取决于音频时长，通常几分钟内完成。

### Q: 支持哪些语言？
A: 支持中文（普通话、粤语、方言）、英文、日语等。

### Q: 如何处理大文件？
A: 单个文件最大支持 500MB，建议先压缩音频。

## License

MIT
