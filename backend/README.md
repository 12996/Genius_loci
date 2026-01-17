# 万物有灵 - 后端服务

基于Flask的后端API服务，集成天气查询、心情分析、魔搭AI和Supabase数据库。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加：
```bash
MODELSCOPE_API_KEY=your_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 3. 初始化数据库

在Supabase的SQL Editor中运行 `supabase_init.sql`

### 4. 测试连接

```bash
python test_database.py
```

### 5. 启动服务

```bash
# Windows
start.bat

# Linux/Mac
./start.sh

# 或手动启动
python app.py
```

---

## 📊 数据表和接口

### 数据表（7个）

| 表名 | 说明 | 主要功能 |
|------|------|----------|
| **users** | 用户表 | 用户信息、设备ID管理 |
| **conversations** | 对话表 | 对话会话管理 |
| **messages** | 消息表 | 聊天消息、上下文信息 |
| **locations** | 位置表 | GPS位置、天气记录 |
| **images** | 图片表 | 图片存储、识别结果 |
| **emotion_history** | 心情表 | 情绪变化历史 |
| **moments** | 时刻表 | 生活时刻记录 |

### API接口（27个）

#### 用户管理
- `POST /api/users` - 创建用户
- `GET /api/users/<id>` - 获取用户
- `GET /api/users/by-device/<id>` - 设备获取
- `PUT /api/users/<id>` - 更新用户

#### 对话管理
- `POST /api/conversations` - 创建对话
- `GET /api/conversations/user/<id>` - 用户对话列表
- `GET /api/conversations/<id>` - 对话详情
- `DELETE /api/conversations/<id>` - 删除对话

#### 消息管理
- `POST /api/messages` - 添加消息
- `GET /api/messages/<conv_id>` - 获取消息
- `GET /api/messages/<conv_id>/recent` - 最近消息

#### Moments
- `POST /api/moments` - 创建Moment
- `GET /api/moments/<id>` - 查询Moment
- `GET /api/moments/user/<id>` - 用户Moments
- `GET /api/moments/nearby` - 附近Moments
- `GET /api/moments/mood/<mood>` - 心情Moments
- `GET /api/moments/recent` - 最近Moments
- `PUT /api/moments/<id>` - 更新Moment
- `DELETE /api/moments/<id>` - 删除Moment
- `POST /api/moments/search` - 搜索Moments

#### 其他
- `POST /api/locations` - 保存位置
- `POST /api/weather` - 查询天气
- `POST /api/emotion` - 分析心情
- `GET /api/stats/*` - 统计数据
- `POST /api/chat` - 智能对话（集成所有功能）

---

## 📁 项目结构

```
backend/
├── app.py                      # Flask主应用
├── config.py                   # 配置文件
├── requirements.txt            # Python依赖
├── .env.example                # 环境变量模板
├── .gitignore                  # Git忽略
│
├── services/                   # 服务模块
│   ├── __init__.py
│   ├── weather_service.py      # 天气服务
│   ├── emotion_service.py      # 心情分析
│   ├── modelscope_service.py   # 魔搭AI
│   ├── supabase_service.py     # 数据库通用服务
│   └── moments_service.py      # Moments专用服务
│
├── supabase_init.sql          # 数据库初始化
│
├── start.bat / start.sh        # 启动脚本
├── test_database.py           # 数据库测试
└── README.md                   # 本文档
```

---

## 🧪 测试

### 运行完整测试

```bash
python test_database.py
```

**测试内容**：
- ✅ 7个数据表的CRUD操作
- ✅ 级联操作（删除对话→删除消息）
- ✅ 批量操作
- ✅ 位置查询
- ✅ 统计分析

---

## 📚 服务使用

### Supabase通用服务

```python
from services import SupabaseService

db = SupabaseService(url, key)

# 用户管理
db.create_user({'username': '张三'})
user = db.get_or_create_user_by_device('device_123')

# 对话管理
conv = db.create_conversation(user_id, '对话标题')
messages = db.get_messages(conv_id)

# 位置记录
db.save_location(user_id, lat, lng, weather_data)
```

### Moments专用服务

```python
from services import MomentsService

moments = MomentsService(client)

# 创建Moment
moments.create_moment(
    user_id, latitude, longitude, input_type,
    media_url, sensor_context, user_mood_tag, ai_narrative
)

# 位置查询
nearby = moments.get_moments_by_location(lat, lng, radius_km=1.0)

# 统计
stats = moments.get_mood_distribution(user_id)
```

---

## 🔧 配置说明

### 环境变量

| 变量 | 说明 | 必填 |
|------|------|------|
| MODELSCOPE_API_KEY | 魔搭API密钥 | 否 |
| SUPABASE_URL | Supabase项目URL | 是 |
| SUPABASE_KEY | Supabase API密钥 | 是 |

### 依赖包

```
Flask==3.0.0
flask-cors==4.0.0
python-dotenv==1.0.0
Pillow==10.1.0
requests==2.31.0
supabase==2.3.4
```

---

## 📝 API使用示例

### 创建Moment

```bash
curl -X POST http://localhost:5000/api/moments \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-uuid",
    "latitude": 39.9042,
    "longitude": 116.4074,
    "input_type": "image",
    "user_mood_tag": "happy"
  }'
```

### 查询附近Moments

```bash
curl "http://localhost:5000/api/moments/nearby?lat=39.9042&lng=116.4074&radius=1"
```

---

## ❓ 常见问题

### Q: 测试失败？

**A**: 检查：
1. `.env` 配置是否正确
2. 数据库表是否已创建（运行supabase_init.sql）
3. 网络连接是否正常

### Q: 如何查看数据？

**A**: 登录Supabase控制台，选择Table Editor查看所有表数据

### Q: 如何部署？

**A**:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

---

## 📚 详细文档

- [SUPABASE_GUIDE.md](SUPABASE_GUIDE.md) - Supabase详细使用指南
- [MOMENTS_GUIDE.md](MOMENTS_GUIDE.md) - Moments服务详细说明

---

## ✨ 更新日志

### v2.0.0 (2024-01-17)
- ✨ 集成Supabase数据库
- ✨ 新增天气查询功能
- ✨ 新增心情分析功能
- ✨ 使用魔搭API
- ✨ 完整的Moments功能
- ✨ 27个API接口
- ✨ 7个数据表
- ✨ 完整测试

---

## 🎯 下一步

1. ✅ 运行 `python test_database.py` 测试所有功能
2. ✅ 启动服务 `python app.py`
3. ✅ 使用API接口进行开发
4. ✅ 查看详细文档了解更多用法

---

## 📞 支持

- 查看测试输出
- 查看Supabase控制台日志
- 参考详细文档
