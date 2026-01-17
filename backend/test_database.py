"""
万物有灵 - 完整数据库功能测试
测试所有数据表的CRUD操作
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from services import SupabaseService, MomentsService
from supabase import create_client, Client 

def print_section(title):
    """打印分隔线"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def print_result(result, show_data=True):
    """打印结果"""
    if result.get('success'):
        print(f"✅ 成功")
        if show_data and result.get('data'):
            if isinstance(result['data'], list):
                print(f"   数量: {len(result['data'])}")
                if len(result['data']) > 0 and len(result['data']) <= 3:
                    for item in result['data'][:3]:
                        print(f"   - {item}")
            else:
                print(f"   数据: {result['data']}")
    else:
        print(f"❌ 失败: {result.get('error')}")

# ==================== 初始化 ====================

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
print(SUPABASE_URL)
print(SUPABASE_KEY)

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ 请配置SUPABASE_URL和SUPABASE_KEY")
    sys.exit(1)

print("=" * 70)
print("万物有灵 - 数据库功能测试")
print("=" * 70)
print(f"\n数据库: {SUPABASE_URL}")
print(f"时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 初始化服务
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)
db = SupabaseService(SUPABASE_URL, SUPABASE_KEY)

moments = MomentsService(supabase)

# 存储测试数据
test_data = {}

try:
    # ==================== 1. users表测试 ====================
    print_section("1. users 表测试")

    print_result(result)
    if result['success']:
        test_data['user_id'] = result['data']['id']

    print("\n[b] 通过device_id获取用户")
    result = db.get_or_create_user_by_device('test_device_001')
    print_result(result)

    if test_data['user_id']:
        print("\n[c] 更新用户")
        result = db.update_user(test_data['user_id'], {'username': '测试用户_已更新'})
        print_result(result)

    # ==================== 2. conversations表测试 ====================
    print_section("2. conversations 表测试")

    if test_data['user_id']:
        print("\n[a] 创建对话")
        result = db.create_conversation(test_data['user_id'], '测试对话')
        print_result(result)
        if result['success']:
            test_data['conversation_id'] = result['data']['id']

        print("\n[b] 获取对话列表")
        result = db.get_conversations(test_data['user_id'])
        print_result(result)

    # ==================== 3. messages表测试 ====================
    print_section("3. messages 表测试")

    if test_data['conversation_id']:
        print("\n[a] 添加消息（含上下文）")
        result = db.add_message(
            conversation_id=test_data['conversation_id'],
            role='user',
            content='测试消息',
            emotion_data={'primary_emotion': 'happy', 'emoji': '😊'},
            weather_data={'temperature': 25, 'description': '晴朗'}
        )
        print_result(result)

        print("\n[b] 获取消息列表")
        result = db.get_messages(test_data['conversation_id'])
        print_result(result)

    # ==================== 4. locations表测试 ====================
    print_section("4. locations 表测试")

    if test_data['user_id']:
        print("\n[a] 保存位置（含天气）")
        result = db.save_location(
            test_data['user_id'],
            latitude=39.9042,
            longitude=116.4074,
            weather_data={'temperature': 25, 'description': '晴朗'}
        )
        print_result(result)

        print("\n[b] 获取位置历史")
        result = db.get_user_locations(test_data['user_id'], limit=10)
        print_result(result)

    # ==================== 5. images表测试 ====================
    print_section("5. images 表测试")

    if test_data['user_id'] and test_data['conversation_id']:
        print("\n[a] 保存图片")
        test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        result = db.save_image(
            test_data['user_id'],
            test_data['conversation_id'],
            test_image,
            {'description': '测试图片'}
        )
        print_result(result)

    # ==================== 6. emotion_history表测试 ====================
    print_section("6. emotion_history 表测试")

    if test_data['user_id']:
        print("\n[a] 创建心情记录")
        try:
            result = client.table('emotion_history').insert({
                'user_id': test_data['user_id'],
                'emotion': 'happy',
                'emotion_data': {'emoji': '😊'},
                'intensity': 0.8,
                'context': '测试记录'
            }).execute()

            if result.data:
                print(f"✅ 成功 - ID: {result.data[0]['id']}")
        except Exception as e:
            print(f"❌ 失败: {e}")

        print("\n[b] 查询心情历史")
        try:
            result = client.table('emotion_history') \
                .select('*') \
                .eq('user_id', test_data['user_id']) \
                .limit(5) \
                .execute()

            print(f"✅ 成功 - 数量: {len(result.data)}")
        except Exception as e:
            print(f"❌ 失败: {e}")

    # ==================== 7. moments表测试 ====================
    print_section("7. moments 表测试")

    print("\n[a] 创建Moment")
    result = moments.create_moment(
        user_id=test_data.get('user_id', 'test-user'),
        latitude=39.9042,
        longitude=116.4074,
        input_type='image',
        media_url='https://example.com/test.jpg',
        sensor_context={'weather': '晴朗'},
        user_mood_tag='happy',
        ai_narrative='测试叙述'
    )
    print_result(result)

    if result['success']:
        test_data['moment_id'] = result['data']['id']

    print("\n[b] 查询用户Moments")
    if test_data.get('user_id'):
        result = moments.get_moments_by_user(test_data['user_id'], limit=10)
        print_result(result)

    print("\n[c] 查询附近Moments")
    result = moments.get_moments_by_location(39.9042, 116.4074, radius_km=10, limit=10)
    print_result(result)

    print("\n[d] 查询最近Moments")
    result = moments.get_recent_moments(limit=10)
    print_result(result)

    # ==================== 8. 统计功能测试 ====================
    print_section("8. 统计功能测试")

    if test_data.get('user_id'):
        print("\n[a] 用户统计")
        result = db.get_user_stats(test_data['user_id'])
        print_result(result)

        print("\n[b] 心情分布")
        result = moments.get_mood_distribution(test_data['user_id'])
        print_result(result)

        print("\n[c] 输入类型分布")
        result = moments.get_input_type_distribution(test_data['user_id'])
        print_result(result)

    # ==================== 9. 批量操作测试 ====================
    print_section("9. 批量操作测试")

    if test_data.get('user_id'):
        print("\n[a] 批量创建Moments")
        moments_data = []
        for i in range(3):
            moments_data.append({
                'user_id': test_data['user_id'],
                'latitude': 39.9042 + i * 0.01,
                'longitude': 116.4074 + i * 0.01,
                'input_type': 'test',
                'user_mood_tag': 'happy'
            })

        result = moments.create_moments_batch(moments_data)
        print_result(result)

    # ==================== 10. 级联删除测试 ====================
    print_section("10. 级联操作测试")

    if test_data.get('conversation_id'):
        print("\n[a] 删除对话（应级联删除消息）")
        result = db.delete_conversation(test_data['conversation_id'])
        print_result(result, show_data=False)

    # ==================== 完成 ====================
    print("\n" + "=" * 70)
    print("✅ 测试完成！")
    print("=" * 70)

    print("\n📊 测试数据摘要:")
    print(f"   用户ID: {test_data.get('user_id', 'N/A')}")
    print(f"   对话ID: {test_data.get('conversation_id', 'N/A')}")
    print(f"   Moment ID: {test_data.get('moment_id', 'N/A')}")

    print("\n💡 提示:")
    print("   - 所有测试数据已保存在数据库中")
    print("   - 可以在Supabase控制台查看")
    print("   - 如需清理请手动删除测试用户")

except KeyboardInterrupt:
    print("\n\n⚠️  测试被中断")
except Exception as e:
    print(f"\n❌ 测试出错: {e}")
    import traceback
    traceback.print_exc()
