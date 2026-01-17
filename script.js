// 全局变量
let currentStream = null;
let currentPosition = null;
let apiClient = null;

// DOM 元素
const homeScreen = document.getElementById('home-screen');
const chatScreen = document.getElementById('chat-screen');
const cameraPreview = document.getElementById('camera-preview');
const photoCanvas = document.getElementById('photo-canvas');
const awakenBtn = document.getElementById('awaken-btn');
const cameraFab = document.getElementById('camera-fab');
const backBtn = document.getElementById('back-btn');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const chatMessages = document.getElementById('chat-messages');
const photoModal = document.getElementById('photo-modal');
const capturedPhoto = document.getElementById('captured-photo');
const closeModal = document.getElementById('close-modal');
const retakeBtn = document.getElementById('retake-btn');
const usePhotoBtn = document.getElementById('use-photo-btn');
const locationText = document.getElementById('location-text');
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initAPI();
    initCamera();
    initGeolocation();
    initEventListeners();
    initDropZone();
});

// 初始化API客户端
async function initAPI() {
    try {
        apiClient = new APIClient();

        // 检查服务器健康状态
        const health = await apiClient.checkHealth();

        if (health.status === 'ok') {
            console.log('✓ 后端服务器连接成功');

            if (health.model_loaded) {
                console.log('✓ AI模型已加载');
            } else {
                console.log('⚠ 使用备用识别方案');
            }
        } else {
            console.warn('⚠ 后端服务器未响应，将使用本地模拟回复');
            apiClient = null;
        }
    } catch (error) {
        console.warn('⚠ 无法连接到后端服务器，将使用本地模拟回复');
        console.log('提示: 运行 python app.py 启动后端服务器');
        apiClient = null;
    }
}

// 初始化相机
async function initCamera() {
    try {
        // 检查是否支持相机
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            console.warn('相机API不支持');
            locationText.textContent = '相机功能不可用';
            return;
        }

        // 请求相机权限
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'environment', // 优先使用后置摄像头
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });

        currentStream = stream;
        cameraPreview.srcObject = stream;

        console.log('相机初始化成功');

    } catch (error) {
        console.error('相机初始化失败:', error);

        // 根据错误类型显示不同提示
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            alert('需要相机权限才能使用拍照功能。请在浏览器设置中允许访问相机。');
        } else if (error.name === 'NotFoundError') {
            alert('未检测到相机设备。');
        } else {
            alert('相机初始化失败: ' + error.message);
        }

        // 显示占位提示
        cameraPreview.style.background = 'linear-gradient(135deg, #E8DED1 0%, #F8F3E9 100%)';
    }
}

// 初始化地理位置
function initGeolocation() {
    if (!navigator.geolocation) {
        locationText.textContent = '地理位置不支持';
        return;
    }

    // 请求位置信息
    navigator.geolocation.getCurrentPosition(
        (position) => {
            currentPosition = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            };

            // 显示位置信息
            locationText.textContent = `${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`;
            console.log('位置获取成功:', currentPosition);
        },
        (error) => {
            console.error('位置获取失败:', error);

            let errorMessage = '位置获取失败';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage = '位置权限被拒绝';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage = '位置信息不可用';
                    break;
                case error.TIMEOUT:
                    errorMessage = '位置请求超时';
                    break;
            }

            locationText.textContent = errorMessage;
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

// 初始化事件监听器
function initEventListeners() {
    // 唤醒按钮
    awakenBtn.addEventListener('click', handleAwaken);
    cameraFab.addEventListener('click', handleCapture);

    // 返回按钮
    backBtn.addEventListener('click', showHomeScreen);

    // 聊天相关
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // 模态框相关
    closeModal.addEventListener('click', closePhotoModal);
    retakeBtn.addEventListener('click', retakePhoto);
    usePhotoBtn.addEventListener('click', usePhoto);

    // 点击模态框背景关闭
    photoModal.addEventListener('click', (e) => {
        if (e.target === photoModal) {
            closePhotoModal();
        }
    });
}

// 处理唤醒按钮点击
function handleAwaken() {
    // 添加动画效果
    awakenBtn.style.transform = 'scale(0.95)';
    setTimeout(() => {
        awakenBtn.style.transform = '';
    }, 150);

    // 切换到聊天界面
    showChatScreen();
}

// 处理拍照
function handleCapture() {
    // 添加动画效果
    cameraFab.style.transform = 'translateX(-50%) scale(0.9)';
    setTimeout(() => {
        cameraFab.style.transform = '';
    }, 150);

    // 检查相机是否可用
    if (!currentStream) {
        alert('相机未初始化，无法拍照');
        return;
    }

    // 设置canvas尺寸与视频流一致
    photoCanvas.width = cameraPreview.videoWidth;
    photoCanvas.height = cameraPreview.videoHeight;

    // 绘制当前帧到canvas
    const ctx = photoCanvas.getContext('2d');
    ctx.drawImage(cameraPreview, 0, 0, photoCanvas.width, photoCanvas.height);

    // 转换为图片数据
    const imageData = photoCanvas.toDataURL('image/png');

    // 显示模态框
    capturedPhoto.src = imageData;
    photoModal.classList.add('active');

    console.log('照片已拍摄');
}

// 关闭照片模态框
function closePhotoModal() {
    photoModal.classList.remove('active');
}

// 重拍
function retakePhoto() {
    closePhotoModal();
}

// 使用照片
async function usePhoto() {
    // 获取图片数据
    const imageData = capturedPhoto.src;

    // 创建一个新的消息显示照片
    addMessage('user', '我拍了一张照片', imageData);

    // 关闭模态框
    closePhotoModal();

    // 切换到聊天界面
    showChatScreen();

    // 如果API可用，调用识别接口
    if (apiClient) {
        try {
            addMessage('spirit', '让我看看这是什么...');

            const result = await apiClient.identifyImage(imageData);

            if (result.success) {
                const responseText = `我识别出来了！这是：${result.description}\n\n其中的物体有：${result.objects.join('、')}`;
                addMessage('spirit', responseText);
            } else {
                addMessage('spirit', '抱歉，我没能识别出这是什么。');
            }
        } catch (error) {
            console.error('识别失败:', error);
            addMessage('spirit', '识别时出错了，但我能感受到这张照片的灵性。');
        }
    } else {
        // 使用本地模拟回复
        setTimeout(() => {
            const responses = [
                '哈哈，拍得不错！这张照片里藏着我的秘密呢。',
                '哎呀，被你拍到了！我正在这里休息呢。',
                '这张照片很有灵性，你能感觉到我的存在吗？',
                '有趣的角度！让我给你讲讲这个地方的故事...'
            ];
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            addMessage('spirit', randomResponse);
        }, 1000);
    }
}

// 显示主屏幕
function showHomeScreen() {
    homeScreen.classList.add('active');
    chatScreen.classList.remove('active');
}

// 显示聊天屏幕
function showChatScreen() {
    homeScreen.classList.remove('active');
    chatScreen.classList.add('active');
}

// 发送消息
function sendMessage() {
    const message = chatInput.value.trim();

    if (!message) {
        return;
    }

    // 添加用户消息
    addMessage('user', message);

    // 清空输入框
    chatInput.value = '';

    // 模拟灵体回应
    setTimeout(() => {
        const response = generateSpiritResponse(message);
        addMessage('spirit', response);
    }, 500 + Math.random() * 1000);
}

// 生成灵体回应
function generateSpiritResponse(userMessage) {
    const responses = {
        '你好': ['你好呀！很高兴见到你。', '嘿，你终于来了！', '你好，我是这里的地灵。'],
        '故事': ['我有好多故事要讲呢，你想听哪个？', '故事啊...让我想想从哪说起好呢。', '我的故事都在茶里呢，要不要来一杯？'],
        '名字': ['我是茶壶地灵，你可以叫我小茶。', '名字？我有很多名字，你叫我什么都可以。'],
        'default': [
            '有趣的问题...让我想想。',
            '嗯嗯，你说得对。',
            '这个问题很有深意呢。',
            '我能感觉到你的真诚。',
            '万物皆有灵，你感受到了吗？',
            '继续说，我在听呢。',
            '哈哈，你真有意思！'
        ]
    };

    // 检查关键词
    for (const [key, value] of Object.entries(responses)) {
        if (key !== 'default' && userMessage.includes(key)) {
            return value[Math.floor(Math.random() * value.length)];
        }
    }

    // 返回默认回应
    return responses.default[Math.floor(Math.random() * responses.default.length)];
}

// 添加消息到聊天界面
function addMessage(type, text, image = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type === 'user' ? 'user-message' : 'spirit-message'} fade-in`;

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';

    if (image) {
        const img = document.createElement('img');
        img.src = image;
        img.style.maxWidth = '100%';
        img.style.borderRadius = '10px';
        img.style.marginBottom = '8px';
        bubbleDiv.appendChild(img);
    }

    const textSpan = document.createElement('span');
    textSpan.textContent = text;
    bubbleDiv.appendChild(textSpan);

    messageDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(messageDiv);

    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 页面卸载时清理资源
window.addEventListener('beforeunload', () => {
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
    }
});

// 处理页面可见性变化
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // 页面隐藏时暂停相机（节省资源）
        if (currentStream) {
            currentStream.getTracks().forEach(track => {
                if (track.kind === 'video') {
                    track.enabled = false;
                }
            });
        }
    } else {
        // 页面显示时恢复相机
        if (currentStream) {
            currentStream.getTracks().forEach(track => {
                if (track.kind === 'video') {
                    track.enabled = true;
                }
            });
        }
    }
});

// 初始化拖拽上传区域
function initDropZone() {
    // 防止默认拖拽行为
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // 添加拖拽效果
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    // 处理文件拖放
    dropZone.addEventListener('drop', handleDrop, false);

    // 处理点击上传
    fileInput.addEventListener('change', handleFileSelect, false);
}

// 阻止默认行为
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// 高亮拖拽区域
function highlight(e) {
    dropZone.classList.add('drag-over');
}

// 取消高亮
function unhighlight(e) {
    dropZone.classList.remove('drag-over');
}

// 处理文件拖放
function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    handleFiles(files);
}

// 处理文件选择
function handleFileSelect(e) {
    const files = e.target.files;
    handleFiles(files);

    // 清空input，允许重复选择同一文件
    fileInput.value = '';
}

// 处理文件
function handleFiles(files) {
    const imageFiles = Array.from(files).filter(file => file.type.startsWith('image/'));

    if (imageFiles.length === 0) {
        alert('请选择图片文件！');
        return;
    }

    // 处理每个图片文件
    imageFiles.forEach((file, index) => {
        const reader = new FileReader();

        reader.onload = (e) => {
            const imageData = e.target.result;

            // 延迟显示，避免同时处理多张图片
            setTimeout(() => {
                // 显示预览模态框
                capturedPhoto.src = imageData;
                photoModal.classList.add('active');

                // 如果是第一张图片，设置模态框按钮行为
                if (index === 0) {
                    // 移除旧的事件监听器
                    const newUsePhotoBtn = usePhotoBtn.cloneNode(true);
                    usePhotoBtn.parentNode.replaceChild(newUsePhotoBtn, usePhotoBtn);

                    // 添加新的事件监听器
                    newUsePhotoBtn.addEventListener('click', () => useUploadedPhoto(imageData));

                    // 更新引用
                    document.getElementById('use-photo-btn').addEventListener('click', () => {
                        useUploadedPhoto(imageData);
                    });
                }
            }, index * 100);
        };

        reader.readAsDataURL(file);
    });
}

// 使用上传的照片
async function useUploadedPhoto(imageData) {
    // 关闭模态框
    closePhotoModal();

    // 添加到聊天界面
    addMessage('user', '我上传了一张图片', imageData);

    // 切换到聊天界面
    showChatScreen();

    // 如果API可用，调用识别接口
    if (apiClient) {
        try {
            addMessage('spirit', '让我看看你上传了什么...');

            const result = await apiClient.identifyImage(imageData);

            if (result.success) {
                const responseText = `我识别出来了！这是：${result.description}\n\n其中的物体有：${result.objects.join('、')}`;
                addMessage('spirit', responseText);
            } else {
                addMessage('spirit', '抱歉，我没能识别出这是什么。');
            }
        } catch (error) {
            console.error('识别失败:', error);
            addMessage('spirit', '识别时出错了，但我能感受到这张照片的灵性。');
        }
    } else {
        // 使用本地模拟回复
        setTimeout(() => {
            const responses = [
                '哦！这张照片很有灵性呢！',
                '哇，我感受到了这张照片里的故事。',
                '有意思，这张照片里好像藏着什么秘密...',
                '好照片！万物皆有灵，你拍到了它的灵魂。',
                '这张照片让我想起了很多往事...'
            ];
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            addMessage('spirit', randomResponse);
        }, 1000);
    }
}
