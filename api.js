/**
 * API配置
 */
const API_CONFIG = {
    baseURL: 'http://localhost:5000',
    endpoints: {
        identify: '/api/identify',
        chat: '/api/chat',
        health: '/health'
    }
};

/**
 * API客户端类
 */
class APIClient {
    constructor(config = API_CONFIG) {
        this.baseURL = config.baseURL;
        this.endpoints = config.endpoints;
    }

    /**
     * 检查服务器健康状态
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseURL}${this.endpoints.health}`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('健康检查失败:', error);
            return { status: 'error', error: error.message };
        }
    }

    /**
     * 识别图片
     * @param {string} imageBase64 - Base64编码的图片
     * @param {string} text - 可选的用户消息
     */
    async identifyImage(imageBase64, text = '') {
        try {
            const response = await fetch(`${this.baseURL}${this.endpoints.identify}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageBase64,
                    text: text
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || '识别失败');
            }

            return data;
        } catch (error) {
            console.error('图片识别失败:', error);
            throw error;
        }
    }

    /**
     * 发送聊天消息
     * @param {string} message - 用户消息
     * @param {string} imageBase64 - 可选的Base64编码图片
     * @param {string} context - 可选的上下文
     */
    async chat(message, imageBase64 = null, context = '') {
        try {
            const payload = {
                message: message,
                context: context
            };

            if (imageBase64) {
                payload.image = imageBase64;
            }

            const response = await fetch(`${this.baseURL}${this.endpoints.chat}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || '聊天失败');
            }

            return data;
        } catch (error) {
            console.error('聊天请求失败:', error);
            throw error;
        }
    }

    /**
     * 将图片文件转换为Base64
     * @param {File} file - 图片文件
     */
    async fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    /**
     * 从canvas或img元素获取Base64图片
     * @param {HTMLCanvasElement|HTMLImageElement} element
     */
    getBase64FromElement(element) {
        if (element.tagName === 'CANVAS') {
            return element.toDataURL('image/png');
        } else if (element.tagName === 'IMG') {
            return element.src;
        }
        throw new Error('不支持的元素类型');
    }
}

// 导出API客户端实例
const apiClient = new APIClient();

// 如果在浏览器环境中，将其添加到window对象
if (typeof window !== 'undefined') {
    window.APIClient = APIClient;
    window.apiClient = apiClient;
}

// Node.js环境导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIClient, apiClient, API_CONFIG };
}
