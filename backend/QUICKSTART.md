# 万物有灵 - 快速启动指南

## 🚀 快速配置（解决httpx冲突）

### Windows用户

直接双击运行：
```
setup_env.bat
```

### 手动配置

```bash
# 1. 激活环境
conda activate things_soul

# 2. 升级httpx（关键步骤）
pip install "httpx>=0.26.0,<0.30.0" --force-reinstall

# 3. 安装依赖
pip install -r requirements.txt

# 4. 测试
python test_database.py
```

## ✅ 依赖说明

### 关键依赖

```
Flask==3.0.0              # Web框架
flask-cors==4.0.0         # 跨域支持
python-dotenv==1.0.0      # 环境变量
Pillow==10.1.0             # 图片处理
requests==2.31.0           # HTTP请求
supabase==2.3.4            # 数据库客户端
httpx>=0.26.0,<0.30.0      # HTTP客户端（重要）
```

### 依赖冲突解决

**问题**：supabase需要httpx>=0.26，但环境有0.25版本

**解决**：强制升级httpx

```bash
pip install "httpx>=0.26.0,<0.30.0" --force-reinstall
```

## 🧪 验证安装

```bash
# 检查httpx版本
pip show httpx

# 检查所有依赖
pip list | findstr "Flask supabase httpx"
```

## 🚀 启动项目

### 测试数据库连接

```bash
python test_database.py
```

### 启动Flask服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动

---

## 🐛 常见问题

### Q1: httpx升级失败

```bash
# 尝试使用conda-forge
pip install httpx -c conda-forge
```

### Q2: 其他依赖冲突

```bash
# 创建干净环境
conda create -n things_soul_clean python=3.9 -y
conda activate things_soul_clean
pip install -r requirements.txt
```

### Q3: Supabase连接失败

- 检查.env文件配置
- 确认表已创建（运行supabase_init.sql）
- 检查网络连接
