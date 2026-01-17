# 万物有灵 (Animism) Web 应用

一个具有温暖大地色调的交互式网页应用，支持桌面端和移动端，具有拍照和地理位置功能。

## 功能特性

### 1. 响应式设计
- 桌面端：大屏幕优化布局
- 平板端：中等屏幕适配
- 手机端：移动优先设计

### 2. 核心功能
- **相机功能**：使用设备相机拍摄照片
- **地理位置**：获取并显示当前地理位置
- **聊天交互**：与虚拟灵体进行对话
- **照片预览**：拍摄后预览并选择使用或重拍

### 3. 界面特点
- 温暖的大地色调配色方案
- 动态光晕效果
- 平滑的动画过渡
- 圆形取景器设计
- 浮动操作按钮（移动端）

## 文件结构

```
all_thins_have_soul/
├── index.html      # 主HTML文件
├── style.css       # 样式表
├── script.js       # JavaScript功能
└── README.md       # 说明文档
```

## 使用方法

### 1. 直接打开
在浏览器中打开 `index.html` 文件即可使用。

### 2. 本地服务器（推荐）
由于浏览器安全限制，某些功能（如相机）可能需要通过本地服务器运行：

#### 使用 Python:
```bash
# Python 3
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000
```

#### 使用 Node.js (http-server):
```bash
npx http-server
```

#### 使用 VSCode Live Server:
安装 Live Server 扩展，右键点击 HTML 文件选择 "Open with Live Server"

### 3. 访问应用
在浏览器中访问 `http://localhost:8000`

## 浏览器兼容性

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- 移动浏览器（iOS Safari, Chrome Mobile）

**注意**：相机和地理位置功能需要：
- HTTPS 环境或 localhost
- 用户授权访问

## 权限说明

应用需要以下权限：
- **相机权限**：用于拍摄照片
- **地理位置权限**：用于获取当前位置

首次使用时，浏览器会请求这些权限，请选择"允许"。

## 主要功能说明

### 拍照功能
1. 点击"点击唤醒万物"按钮（桌面端）或浮动相机按钮（移动端）
2. 相机预览会显示在圆形取景器中
3. 点击拍照按钮捕获当前画面
4. 在预览窗口选择"使用这张照片"或"重拍"
5. 照片会发送到聊天界面

### 地理位置功能
- 自动获取当前地理位置
- 显示在页面左下角
- 格式：纬度, 经度

### 聊天功能
- 在输入框中输入消息
- 点击发送按钮或按 Enter 键发送
- 虚拟灵体会自动回复

## 技术栈

- HTML5
- CSS3（Flexbox, Grid, Animations）
- Vanilla JavaScript（ES6+）
- MediaDevices API（相机）
- Geolocation API（位置）

## 自定义配置

### 修改颜色主题
在 `style.css` 中修改 CSS 变量：

```css
:root {
    --primary-bg: #F8F3E9;
    --accent-gold: #D4AF37;
    --warm-brown: #B8860B;
    /* ... 其他颜色 */
}
```

### 修改聊天回应
在 `script.js` 中的 `generateSpiritResponse` 函数中添加自定义回应。

## 常见问题

### Q: 相机无法启动？
A: 确保：
1. 使用 HTTPS 或 localhost
2. 已授予相机权限
3. 设备有可用的相机

### Q: 地理位置显示错误？
A: 检查：
1. 是否授予了位置权限
2. 设备的定位服务是否开启
3. 浏览器是否支持地理位置

### Q: 移动端显示不正常？
A: 确保在 HTML 头部包含正确的 viewport 设置：
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

## 开发建议

### 测试响应式设计
使用浏览器开发者工具的设备模拟功能：
1. 打开开发者工具（F12）
2. 点击设备工具栏图标
3. 选择不同的设备进行测试

### 调试相机功能
在控制台查看日志：
```javascript
console.log('相机初始化成功');
console.log('位置获取成功:', currentPosition);
```

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎反馈。
