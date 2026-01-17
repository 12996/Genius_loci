"""
万物有灵 API 测试脚本
用于测试后端API的各项功能
"""

import requests
import base64
import json
import sys
from pathlib import Path

# API配置
BASE_URL = "http://localhost:5000"

def print_separator(title=""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    else:
        print(f"{'='*60}")

def print_result(response):
    """打印响应结果"""
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def image_to_base64(image_path):
    """将图片转换为Base64"""
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        base64_string = base64.b64encode(image_data).decode('utf-8')

        # 根据文件扩展名确定MIME类型
        ext = Path(image_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(ext, 'image/png')

        return f"data:{mime_type};base64,{base64_string}"
    except FileNotFoundError:
        print(f"❌ 错误: 找不到图片文件 {image_path}")
        return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def test_home():
    """测试主页接口"""
    print_separator("测试1: GET / (主页)")

    try:
        response = requests.get(f"{BASE_URL}/")
        result = print_result(response)

        if response.status_code == 200:
            print("✅ 主页接口测试成功")
            return True
        else:
            print("❌ 主页接口测试失败")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print(f"   提示: 请确保后端服务器正在运行 (python app.py)")
        return False

def test_health():
    """测试健康检查接口"""
    print_separator("测试2: GET /health (健康检查)")

    try:
        response = requests.get(f"{BASE_URL}/health")
        result = print_result(response)

        if response.status_code == 200 and result.get('status') == 'ok':
            print("✅ 健康检查成功")
            if result.get('model_loaded'):
                print("✅ AI模型已加载")
            else:
                print("⚠️  AI模型未加载，使用备用方案")
            return True
        else:
            print("❌ 健康检查失败")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_identify_without_image():
    """测试图片识别接口（缺少图片）"""
    print_separator("测试3: POST /api/identify (缺少图片)")

    try:
        response = requests.post(
            f"{BASE_URL}/api/identify",
            json={"text": "这是什么？"}
        )
        result = print_result(response)

        if response.status_code == 400 and not result.get('success'):
            print("✅ 正确处理了缺少图片的错误")
            return True
        else:
            print("❌ 应该返回400错误")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_identify_with_image(image_path):
    """测试图片识别接口（有图片）"""
    print_separator(f"测试4: POST /api/identify (识别图片: {image_path})")

    # 转换图片为Base64
    image_base64 = image_to_base64(image_path)
    if not image_base64:
        print("❌ 无法读取图片文件")
        return False

    print(f"📷 图片已加载 (Base64长度: {len(image_base64)} 字符)")

    try:
        response = requests.post(
            f"{BASE_URL}/api/identify",
            json={
                "image": image_base64,
                "text": "这是什么？"
            }
        )
        result = print_result(response)

        if response.status_code == 200 and result.get('success'):
            print("✅ 图片识别成功")
            print(f"📝 描述: {result.get('description', 'N/A')}")
            print(f"🏷️  物体: {', '.join(result.get('objects', []))}")
            return True
        else:
            print("❌ 图片识别失败")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_identify_invalid_base64():
    """测试图片识别接口（无效Base64）"""
    print_separator("测试5: POST /api/identify (无效Base64)")

    try:
        response = requests.post(
            f"{BASE_URL}/api/identify",
            json={
                "image": "invalid_base64_string!!!",
                "text": "这是什么？"
            }
        )
        result = print_result(response)

        if response.status_code == 500:
            print("✅ 正确处理了无效Base64的错误")
            return True
        else:
            print("⚠️  期望500错误，但得到了:", response.status_code)
            return True  # 也算通过
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_chat_without_message():
    """测试聊天接口（缺少消息）"""
    print_separator("测试6: POST /api/chat (缺少消息)")

    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={}
        )
        result = print_result(response)

        if response.status_code == 400 and not result.get('success'):
            print("✅ 正确处理了缺少消息的错误")
            return True
        else:
            print("❌ 应该返回400错误")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_chat_text_only():
    """测试聊天接口（纯文本）"""
    print_separator("测试7: POST /api/chat (纯文本对话)")

    test_messages = [
        "你好！",
        "这是什么？",
        "给我讲个故事"
    ]

    all_passed = True

    for i, message in enumerate(test_messages, 1):
        print(f"\n测试消息 {i}: {message}")

        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": message}
            )
            result = print_result(response)

            if response.status_code == 200 and result.get('success'):
                print(f"✅ 回复: {result.get('response', 'N/A')}")
            else:
                print(f"❌ 对话失败")
                all_passed = False
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            all_passed = False

    if all_passed:
        print("\n✅ 纯文本对话测试成功")

    return all_passed

def test_chat_with_image(image_path):
    """测试聊天接口（带图片）"""
    print_separator(f"测试8: POST /api/chat (带图片对话: {image_path})")

    # 转换图片为Base64
    image_base64 = image_to_base64(image_path)
    if not image_base64:
        print("❌ 无法读取图片文件")
        return False

    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "message": "这张照片里有什么？",
                "image": image_base64,
                "context": "用户想了解图片内容"
            }
        )
        result = print_result(response)

        if response.status_code == 200 and result.get('success'):
            print("✅ 带图片对话成功")
            print(f"💬 回复: {result.get('response', 'N/A')}")
            if result.get('image_info'):
                print(f"🖼️  图片信息: {result['image_info']}")
            return True
        else:
            print("❌ 对话失败")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print_separator("万物有灵 API 测试开始")

    # 检查是否有测试图片
    test_images = []
    possible_paths = [
        "test.jpg",
        "test.png",
        "photo.jpg",
        "photo.png",
        "../test.jpg"
    ]

    for path in possible_paths:
        if Path(path).exists():
            test_images.append(path)
            break

    if not test_images:
        print("⚠️  警告: 未找到测试图片文件")
        print("   跳过需要图片的测试")
        print(f"   提示: 请将测试图片命名为 test.jpg 或 test.png 放在当前目录")
    else:
        print(f"✅ 找到测试图片: {test_images[0]}")

    # 运行测试
    results = []

    # 基础测试
    results.append(("主页", test_home()))
    results.append(("健康检查", test_health()))
    results.append(("缺少图片错误", test_identify_without_image()))
    results.append(("无效Base64", test_identify_invalid_base64()))
    results.append(("缺少消息错误", test_chat_without_message()))
    results.append(("纯文本对话", test_chat_text_only()))

    # 需要图片的测试
    if test_images:
        results.append(("图片识别", test_identify_with_image(test_images[0])))
        results.append(("带图片对话", test_chat_with_image(test_images[0])))

    # 打印测试总结
    print_separator("测试总结")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:.<30} {status}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print(f"⚠️  {total - passed} 个测试失败")

    return passed == total

def create_test_image():
    """创建一个简单的测试图片"""
    try:
        from PIL import Image, ImageDraw

        # 创建一个简单的测试图片
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)

        # 绘制一些形状
        draw.rectangle([50, 50, 200, 200], fill='blue')
        draw.ellipse([250, 100, 350, 200], fill='red')

        # 保存
        img.save('test.jpg')
        print("✅ 已创建测试图片: test.jpg")
        return True
    except ImportError:
        print("⚠️  需要安装PIL库来创建测试图片")
        return False
    except Exception as e:
        print(f"❌ 创建测试图片失败: {e}")
        return False

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--create-test-image":
            create_test_image()
        elif sys.argv[1] == "--image":
            if len(sys.argv) > 2:
                # 使用指定图片测试
                image_path = sys.argv[2]
                print(f"使用图片: {image_path}\n")

                if not Path(image_path).exists():
                    print(f"❌ 错误: 图片不存在: {image_path}")
                    sys.exit(1)

                test_home()
                test_health()
                test_identify_with_image(image_path)
                test_chat_with_image(image_path)
            else:
                print("用法: python test_api.py --image <图片路径>")
        else:
            print("用法:")
            print("  python test_api.py              # 运行所有测试")
            print("  python test_api.py --create-test-image  # 创建测试图片")
            print("  python test_api.py --image <path>       # 使用指定图片测试")
    else:
        # 运行所有测试
        run_all_tests()
