"""
测试 Supabase 配置
验证数据库连接是否正常
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# 加载环境变量
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

print("=" * 60)
print("Supabase 配置测试")
print("=" * 60)

# 检查配置
print(f"\n1. 检查环境变量:")
print(f"   SUPABASE_URL: {SUPABASE_URL[:50]}..." if SUPABASE_URL else "   SUPABASE_URL: ❌ 未配置")
print(f"   SUPABASE_KEY: {SUPABASE_KEY[:50]}..." if SUPABASE_KEY else "   SUPABASE_KEY: ❌ 未配置")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("\n❌ 配置不完整，请在 .env 文件中设置 SUPABASE_URL 和 SUPABASE_KEY")
    exit(1)

# 验证 key 格式
print(f"\n2. 验证 API key 格式:")
if SUPABASE_KEY.startswith('eyJ'):
    print(f"   ✓ Key 格式正确（JWT token）")
else:
    print(f"   ⚠ Key 格式可能不正确，应该以 'eyJ' 开头")
    print(f"   当前 key 前缀: {SUPABASE_KEY[:20]}")

# 尝试连接
print(f"\n3. 测试数据库连接:")
try:
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"   ✓ Supabase 客户端创建成功")

    # 尝试简单查询
    result = client.table('users').select('id').limit(1).execute()
    print(f"   ✓ 数据库查询成功")
    print(f"   查询结果: {result.data if result.data else '空（正常）'}")

    print(f"\n✅ Supabase 配置正确，数据库连接正常！")

except Exception as e:
    print(f"   ❌ 数据库连接失败: {e}")
    print(f"\n可能的原因:")
    print(f"   1. API key 不正确或已过期")
    print(f"   2. 项目 URL 不正确")
    print(f"   3. 网络连接问题")
    print(f"   4. Supabase 项目已暂停")
    print(f"\n请检查:")
    print(f"   - .env 文件中的 SUPABASE_URL 和 SUPABASE_KEY")
    print(f"   - Supabase 控制台中的 API 设置")

print("=" * 60)
