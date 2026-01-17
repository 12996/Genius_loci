# 解决httpx依赖冲突的补充说明

## 问题分析

错误信息：
```
supabase-auth 2.27.2 requires httpx[http2]<0.29,>=0.26
but you have httpx 0.25.2 which is incompatible
```

**原因**：Supabase 2.27.2需要httpx >= 0.26，但conda环境中是0.25.2

## 解决方案

### 方案1：强制升级httpx（推荐）

```bash
conda activate things_soul

# 升级httpx
pip install "httpx>=0.26.0,<0.30.0" --force-reinstall

# 重新安装Supabase
pip install supabase==2.3.4 --force-reinstall
```

### 方案2：降级Supabase（不推荐）

```bash
pip install "supabase==2.3.4"
```

### 方案3：使用conda-forge（可能旧版本）

```bash
conda activate things_soul
pip install httpx -c conda-forge
pip install -r requirements.txt
```

### 方案4：创建新环境（最干净）

```bash
# 创建新环境
conda create -n things_soul_clean python=3.9 -y

# 激活
conda activate things_soul_clean

# 安装依赖
pip install -r requirements.txt
```

## 验证安装

```bash
# 检查httpx版本
pip show httpx

# 应该显示: httpx 0.26.0 或更高

# 检查依赖关系
pip check
```

## 预期输出

成功的安装应该类似：
```
Successfully installed httpx-0.26.0
Successfully installed supabase-2.3.4
```

## 完整步骤

### Windows（推荐）

1. 双击 `setup_env.bat`
2. 等待完成
3. 运行 `python test_database.py` 测试

### Linux/Mac

```bash
# 创建脚本
cat > setup_env.sh << 'EOF'
#!/bin/bash
conda activate things_soul
pip install "httpx>=0.26.0,<0.30.0" --force-reinstall
pip install -r requirements.txt
echo "配置完成！"
EOF

chmod +x setup_env.sh

# 运行
./setup_env.sh
```

## 验证项目运行

```bash
# 1. 测试数据库
python test_database.py

# 2. 启动服务
python app.py

# 3. 访问
# 浏览器打开 http://localhost:5000
```

## 附加说明

### 如果还有冲突

删除现有包重装：
```bash
pip uninstall httpx supabase -y
pip install "httpx>=0.26.0,<0.30.0"
pip install "supabase==2.3.4"
```

### 使用pip-tools（更智能的依赖解析）

```bash
pip install pip-tools
pip install -r requirements.txt
```

---

## 测试清单

运行以下命令确保一切正常：

```bash
# 1. 检查环境
python --version
# 应该显示: Python 3.9.x

# 2. 检查httpx
pip show httpx | findstr Version
# 应该显示: 0.26.0 或更高

# 3. 检查Supabase
python -c "from supabase import create_client; print('Supabase导入成功')"

# 4. 测试数据库
python test_database.py
```
