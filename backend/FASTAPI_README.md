# 万物有灵 - FastAPI 后端服务使用说明

## 功能概述

这是一个基于 FastAPI 的智能对话服务，具有以下功能：

1. **天气查询**：根据经纬度获取实时天气信息
2. **心情分析**：分析用户消息中的情绪状态
3. **流式智能对话**：以地灵的身份与用户进行自然对话
4. **对话记忆**：保存和检索用户在特定位置的对话历史

## 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

## 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 魔搭API配置（必需，用于智能对话）
MODELSCOPE_API_KEY=your_api_key_here

# Supabase配置（可选，用于存储对话记忆）
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# 服务器配置
FLASK_ENV=development
FLASK_PORT=8000
```

## 启动服务

### 方式一：使用 Uvicorn

```bash
cd backend
python fastapi_app.py
```

### 方式二：使用 Uvicorn 命令

```bash
cd backend
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问：http://localhost:8000

## API 接口文档

启动服务后，访问以下地址查看完整的 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要 API 接口

### 1. 流式智能对话（主要接口）

**接口**: `POST /api/chat/stream`

**请求体**:
```json
{
  "message": "今天天气真好，心情很愉快",
  "latitude": 39.9042,
  "longitude": 116.4074,
  "uid": "user_unique_id",
  "conversation_id": 123,
  "image": "base64_encoded_image (optional)"
}
```

**响应格式**: Server-Sent Events (SSE)

响应数据流包含以下类型：

1. `start` - 开始标记，包含分析结果
2. `content` - 内容块
3. `end` - 结束标记，包含对话ID
4. `error` - 错误信息

**示例响应**:
```
data: {"type":"start","emotion_analysis":{"primary_emotion":"happy"},"weather_info":"当前天气晴朗，温度25°C"}

data: {"type":"content","content":"风"}

data: {"type":"content","content":"会带来"}

data: {"type":"content","content":"消息"}

data: {"type":"end","conversation_id":123}
```

### 2. 天气查询

**接口**: `POST /api/weather`

**请求体**:
```json
{
  "latitude": 39.9042,
  "longitude": 116.4074
}
```

**响应**:
```json
{
  "success": true,
  "current": {
    "temperature": 25,
    "humidity": 60,
    "weather_description": "晴朗"
  }
}
```

### 3. 心情分析

**接口**: `POST /api/emotion`

**请求体**:
```json
{
  "text": "我今天很开心"
}
```

**响应**:
```json
{
  "success": true,
  "primary_emotion": "happy",
  "description": "心情愉悦",
  "emoji": "😊"
}
```

## 前端集成示例

### 使用 Fetch API（流式接收）

```javascript
async function chatWithStream(message, latitude, longitude, uid) {
  const response = await fetch('http://localhost:8000/api/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      latitude,
      longitude,
      uid
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));

        if (data.type === 'start') {
          console.log('开始分析:', data.emotion_analysis);
          console.log('天气:', data.weather_info);
        } else if (data.type === 'content') {
          // 逐步显示内容
          console.log(data.content);
        } else if (data.type === 'end') {
          console.log('对话完成，对话ID:', data.conversation_id);
        } else if (data.type === 'error') {
          console.error('错误:', data.error);
        }
      }
    }
  }
}

// 使用示例
chatWithStream(
  '今天天气真好',
  39.9042,
  116.4074,
  'user_12345'
);
```

### 使用 EventSource（仅支持 GET）

由于 EventSource 不支持 POST 请求，建议使用 Fetch API 或 WebSocket。

### 使用 Axios

```javascript
import axios from 'axios';

async function chatWithStream(message, latitude, longitude, uid) {
  try {
    const response = await axios.post(
      'http://localhost:8000/api/chat/stream',
      {
        message,
        latitude,
        longitude,
        uid
      },
      {
        responseType: 'stream',
        headers: {
          'Accept': 'text/event-stream'
        }
      }
    );

    response.data.on('data', (chunk) => {
      const text = chunk.toString();
      // 处理 SSE 数据
      console.log(text);
    });

  } catch (error) {
    console.error('Error:', error);
  }
}
```

## 地灵人设说明

地灵是服务中的智能助手角色，具有以下特点：

- **身份**：活了很久的具有大智慧、平和的地灵
- **性格**：温和、智慧、富有同理心
- **语气**：平和温柔，像春风化雨
- **智慧来源**：对天地自然的深刻观察和体悟
- **回复风格**：简洁而深刻，通常在100字以内

### 示例回复

- "风会带走你的烦恼，雨会滋润你的心田。"
- "万物都有它的时节，你的心情也是自然的律动。"
- "这片土地记得每一个故事，我在听，也在感受。"
- "每一刻的呼吸都是与大地的对话，你感受到了吗？"

## 对话记忆功能

服务会根据用户的 `uid` 和经纬度信息保存和检索对话记忆：

1. **记忆存储**：每次对话都会保存到数据库
2. **记忆检索**：下次对话时会自动获取之前的对话上下文
3. **位置关联**：同一位置的对话会被关联在一起

## 注意事项

1. **API Key**：需要配置魔搭 API 才能使用智能对话功能
2. **数据库**：如果配置了 Supabase，对话记忆会被持久化保存
3. **流式输出**：前端需要正确处理 SSE 格式的响应
4. **CORS**：生产环境需要正确配置 CORS 允许的域名

## 开发调试

启用自动重载：

```bash
uvicorn fastapi_app:app --reload
```

查看日志：

服务会输出详细的日志信息，包括：
- 用户请求
- API 调用
- 错误信息

## 常见问题

### 1. 流式输出卡住

检查前端是否正确读取响应流，确保不使用缓冲。

### 2. CORS 错误

在 `fastapi_app.py` 中配置正确的 `allow_origins`。

### 3. 对话记忆不工作

检查 Supabase 配置是否正确，数据库表是否已创建。

### 4. 模型响应慢

- 检查网络连接
- 考虑使用更快的模型
- 减少上下文长度

## 生产部署

### 使用 Gunicorn + Uvicorn

```bash
pip install gunicorn
gunicorn fastapi_app:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 使用 Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 技术栈

- **FastAPI**：现代、快速的 Python Web 框架
- **Uvicorn**：ASGI 服务器
- **Pydantic**：数据验证和设置管理
- **Supabase**：数据库和认证服务
- **Open-Meteo**：天气数据 API
- **魔搭 API**：大语言模型服务

## 许可证

MIT License
