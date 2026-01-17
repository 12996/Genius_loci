"""
启动脚本
运行 FastAPI 服务器
"""
import uvicorn
import os
from config import config

# 获取配置
env = os.getenv('ENV', 'development')
cfg = config[env]

# 启动服务器
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=cfg.PORT,
        reload=cfg.DEBUG,
        log_level="info",
        access_log=True
    )
