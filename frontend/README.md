# RKLLM Frontend - 快速开始指南

## 概述

这是一个为 RKLLM Vision-Language Model 设计的现代 Web 前端，提供完整的多模态交互体验。前端与现有的 RKLLM 服务解耦，可独立部署和升级。

**版本信息：** 已集成 API 代理层，完全解决跨域问题 ✅

## 功能特性

- ✅ **文本输入** - 通过文本框提问
- ✅ **图片上传** - 本地图片或网络 URL
- ✅ **流式输出** - 实时显示 AI 回答
- ✅ **上下文管理** - 侧栏显示对话历史
- ✅ **清爽 UI** - 现代化深色主题，Tailwind CSS 设计
- ✅ **无缝集成** - 通过 OpenAI 兼容 API 通信

## 架构

```
┌──────────────────────────────────┐
│   Web Browser (HTML/JS/CSS)      │
│   Origin: http://10.0.88.51:8000 │
└──────────────────┬───────────────┘
                   │ Same-Origin (无CORS问题)
                   ↓
┌─────────────────────────────────────────┐
│   Flask Frontend Server (Port 8000)     │
│   ✓ 提供静态文件和HTML               │
│   ✓ /api/config - 配置端点             │
│   ✓ /api/backend/* - API代理层        │
│   ✓ CORS 中间件本地配置               │
└──────────────┬────────────────────────┘
               │ Localhost Proxy
               ↓ (无CORS问题)
┌──────────────────────────────────┐
│  RKLLM Backend (Port 8080)       │
│  /v1/chat/completions           │
│  - 支持流式 & 非流式             │
│  - 多模态处理                    │
└──────────────────────────────────┘
```

**关键特性：**
- 浏览器 → 前端：Same-origin，无跨域问题
- 前端 → 后端：通过本地代理，无跨域问题
- 支持局域网访问 (http://192.168.x.x:8000)
- 完全透明的 API 代理

## 目录结构

```
frontend/
├── app.py                  # Flask 服务器入口
├── requirements.txt        # Python 依赖
├── test.py                # 集成测试脚本
├── README.md              # 本文档
├── templates/
│   └── index.html        # 主页面（HTML+CSS+JS）
└── static/
    ├── api.js            # OpenAI API 通信层
    └── main.js           # 前端业务逻辑
```

## 快速开始

### 方式 A：使用启动脚本（推荐）

**Python 版本（跨平台）：**
```bash
cd /home/cat/llm/rkllm-openai/frontend
conda activate llm_api1
python3 start.py
```

**Shell 版本（Linux/Mac）：**
```bash
cd /home/cat/llm/rkllm-openai/frontend
conda activate llm_api1
bash start.sh both        # 启动前后端
# 或
bash start.sh backend     # 仅启动后端
bash start.sh frontend    # 仅启动前端
```

启动脚本会自动：
- ✅ 检查端口可用性
- ✅ 启动后端和前端服务
- ✅ 等待服务就绪
- ✅ 显示访问地址
- ✅ 优雅地关闭（Ctrl+C）

### 方式 B：手动启动

### 方式 B：手动启动

**1. 安装依赖**

```bash
cd /home/cat/llm/rkllm-openai/frontend
conda activate llm_api1
pip install -r requirements.txt
```

**2. 启动后端服务**

```bash
cd /home/cat/llm/rkllm-openai
conda activate llm_api1
python3 main.py
# 监听 0.0.0.0:8080
```

**3. 启动前端服务（新终端）**

```bash
cd /home/cat/llm/rkllm-openai/frontend
conda activate llm_api1
python3 app.py
# 监听 0.0.0.0:8000（默认）
```

**4. 访问前端**

在浏览器打开：
- **本机访问**: http://localhost:8000
- **局域网访问**: http://<机器IP>:8000 (例如 http://10.0.88.51:8000)

## 使用说明

### 启动脚本说明

**Python 启动脚本 (`start.py`)**

自动管理前后端生命周期：
```bash
# 启动所有服务（推荐）
python3 start.py

# 输出示例：
# ✓ All services started successfully!
# 📝 Access the frontend at:
#   - Local:      http://localhost:8000
#   - Network:    http://<your-ip>:8000
# 💡 Press Ctrl+C to stop all services
```

特性：
- 自动检测端口占用
- 如果服务已运行，仅启动缺失的服务
- 等待服务就绪后才显示成功消息
- Ctrl+C 优雅关闭

**Shell 启动脚本 (`start.sh` - Linux/Mac)**

```bash
bash start.sh both        # 启动前后端
bash start.sh backend     # 仅启动后端
bash start.sh frontend    # 仅启动前端
```

相同的智能检测和优雅关闭机制。

### 基础功能

| 功能 | 说明 |
|------|------|
| **📝 文本输入** | 在输入框输入问题，支持中文和英文 |
| **📸 图片选择** | 点击"Image"按钮上传本地图片 |
| **🚀 发送** | 点击"Send"或按 Enter 发送消息 |
| **⏸️ 流式显示** | 回答逐字显示，无需等待完成 |
| **📋 上下文窗口** | 右侧栏显示对话历史和统计信息 |
| **🗑️ 清空历史** | 点击"Clear Context"重新开始 |

### 图片输入方式

**方式1：直接上传本地文件**
```
1. 在聊天界面点击 📸 Image 按钮
2. 选择电脑上的图片文件
3. 图片预览显示后，输入问题
4. 点击 Send 发送
```

**方式2：使用网络 URL**（通过后端处理）
- 当前前端版本不直接支持 URL 输入框
- 可通过命令行脚本传递：
  ```bash
  python3 demo/example_vlm_stream.py \
    --image-url "http://example.com/image.jpg" \
    --prompt "这是什么？"
  ```

## 环境变量配置

可以通过环境变量自定义前端行为：

```bash
# 前端配置
export FRONTEND_HOST=0.0.0.0        # 监听地址（默认 0.0.0.0）
export FRONTEND_PORT=8000           # 监听端口（默认 8000）
export FLASK_DEBUG=False            # 调试模式（默认 False）

# 后端配置（前端会使用）
export RKLLM_API_BASE_URL=http://localhost:8080/v1
export RKLLM_API_KEY=none           # API 密钥
export RKLLM_MODEL_NAME=rkllm-model # 模型名称
export RKLLM_MAX_CONTEXT=4096       # 最大上下文长度

# 然后启动
python3 app.py
```

## 测试

运行完整的集成测试：

```bash
cd /home/cat/llm/rkllm-openai/frontend
conda activate llm_api1
python3 test.py
```

**测试项目：**
1. ✓ 前端主页加载
2. ✓ 配置 API 返回
3. ✓ 健康检查端点
4. ✓ 纯文本查询
5. ✓ 流式查询
6. ✓ 图片+文本查询

**预期结果：** ALL TESTS PASSED (6/6 - 100%)

## 常见问题

### Q: 页面可以打开但消息发送失败？
**A:** 这通常是网络或配置问题。按顺序检查：

1. **检查浏览器控制台**（F12）
   - 是否有 JavaScript 错误
   - 网络标签中是否显示 failed 请求

2. **验证服务在运行**
   ```bash
   ss -tlnp 2>/dev/null | grep -E "(8000|8080)"
   # 应该显示两个 LISTEN 状态的 python3 进程
   ```

3. **直接测试代理 API**
   ```bash
   curl -X POST http://localhost:8000/api/backend/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model":"rkllm-model","messages":[{"role":"user","content":[{"type":"text","text":"test"}]}],"stream":false}'
   # 应该返回 JSON 响应
   ```

4. **重启所有服务**
   ```bash
   cd /home/cat/llm/rkllm-openai/frontend
   python3 start.py
   ```

### Q: 如何在局域网其他设备访问？
**A:** 使用机器的 IP 地址访问（而不是 localhost）

```
http://<你的机器IP>:8000
例如：http://10.0.88.51:8000
```

前端会自动代理到后端，无需配置。

### Q: 连接被拒绝？
**A:** 检查两个服务是否都在运行
```bash
ss -tlnp | grep -E "(8000|8080)"
```

应该显示两个 LISTEN 状态的 python3 进程。

### Q: 图片加载失败？
**A:** 
- 检查图片格式（支持 JPG、PNG、WebP）
- 检查图片大小（限制 10MB）
- 查看浏览器控制台的错误消息（F12）

### Q: 回答很慢？
**A:** 这是正常的，RKLLM 在 ARM CPU 上运行推理，推理时间取决于：
- 模型大小（2B vs 4B）
- 输出长度
- 硬件性能

### Q: 可以修改模型吗？
**A:** 是的，编辑 `/home/cat/llm/rkllm-openai/config.yaml`，修改 MODEL_PATH 后重启后端

## 高级配置

### 1. 跨域访问（公网部署）

如果需要从其他域名访问前端，已配置 CORS 支持。前端自动处理 localhost 和任意 IP 的请求。

### 2. 性能优化

- **增加并发**: 修改 Flask 的 threaded 参数
- **启用缓存**: 在 app.py 中添加 Flask-Caching
- **负载均衡**: 使用 Nginx 反向代理多个前端实例

### 3. 自定义样式

编辑 `templates/index.html` 中的 `<style>` 部分，修改：
- 颜色主题
- 布局宽度
- 动画效果

## 文件说明

### 启动脚本

| 文件 | 说明 | 用途 |
|------|------|------|
| `start.py` | Python 启动管理器 | 跨平台启动（Windows/Linux/Mac） |
| `start.sh` | Shell 启动脚本 | Linux/Mac 快速启动 |

### app.py - Flask 应用入口（含 API 代理）
- **静态服务**: 提供 HTML、CSS、JavaScript
- **配置 API** (`/api/config`): 返回前端配置，API 基础 URL 指向代理端点
- **健康检查** (`/health`): 服务状态检查
- **代理层** (`/api/backend/<path>`): 
  - 将所有 RKLLM API 请求代理到后端 (8080)
  - 支持流式和非流式请求
  - 自动处理 SSE 事件流格式
  - 消除了跨域请求问题

### 启动脚本原理

**start.py 的工作流程：**
```
1. 检查端口可用性
   ├─ 8080 已占用 → 跳过后端启动
   ├─ 8000 已占用 → 跳过前端启动
   └─ 都空闲 → 都启动

2. 启动后端服务 (main.py)
   ├─ 在后台运行进程
   ├─ 等待 /v1/models 端点响应（最多 30 秒）
   └─ 成功时继续

3. 启动前端服务 (app.py)
   ├─ 在后台运行进程
   ├─ 等待主页响应（最多 30 秒）
   └─ 成功时显示就绪消息

4. 监控进程状态
   ├─ 每 2 秒检查一次
   └─ 如果进程退出则立即通知用户

5. 优雅关闭（Ctrl+C）
   ├─ 依次 terminate 每个进程
   ├─ 等待 5 秒（超时则强制 kill）
   └─ 清理资源退出
```

**关键特性：**
- **智能检测** - 如果服务已运行，仅启动缺失的服务
- **超时管理** - 防止无限等待
- **错误显示** - 启动失败时显示日志前几行
- **进程监控** - 持续监控运行中的服务
- **优雅关闭** - Ctrl+C 安全关闭，清理资源

### static/api.js - API 通信层（已改进）
- `RKLLMClient` 类封装 API 调用
- 支持流式和非流式请求
- 自动处理 SSE 事件流格式
- 详细的错误日志输出
- 调试信息：
  - 请求 URL、方法、请求体
  - 响应状态码
  - 网络错误详细信息

### 代理机制工作流程

**浏览器调用流程：**

```
1. 浏览器加载页面
   GET http://10.0.88.51:8000/  ← main.js 加载

2. JavaScript 获取配置
   GET http://10.0.88.51:8000/api/config
   ← 返回 {"api_base_url": "/api/backend", ...}

3. 用户发送消息
   POST http://10.0.88.51:8000/api/backend/chat/completions
   (Same-origin，无 CORS 问题 ✓)

4. 前端代理转发
   Flask 收到请求 → 转发到
   POST http://localhost:8080/v1/chat/completions
   (Localhost，无 CORS 问题 ✓)

5. 后端响应
   Flask 接收响应 → 返回给浏览器
   浏览器 JavaScript 处理响应并显示
```

**关键优势：**
- ✓ 浏览器无 CORS 问题（same-origin）
- ✓ 前端代理层对浏览器完全透明
- ✓ 支持流式响应传输
- ✓ 易于调试：所有请求对开发者工具可见

### static/main.js - 业务逻辑
- 点击事件处理
- 消息渲染和显示
- 上下文窗口管理
- 图片预览和上传

### templates/index.html - 页面结构
- Tailwind CSS（从 CDN 加载）
- 语义化 HTML 布局
- 响应式设计

## 依赖关系

| 包 | 版本 | 用途 |
|----|------|------|
| Flask | 3.0.0 | Web 框架 |
| flask-cors | 4.0.0 | CORS 支持 |
| Werkzeug | 3.0.1 | WSGI 工具库 |

所有依赖都已在 `llm_api1` conda 环境中安装。

## 部署建议

### 开发环境
```bash
python3 app.py
# 访问 http://localhost:8000
```

### 生产环境
```bash
# 使用 gunicorn（需额外安装）
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# 或使用 nginx 反向代理 + Flask 后台运行
nohup python3 app.py > frontend.log 2>&1 &
```

## 故障排查

**查看运行日志：**
```bash
# 前端日志
ps aux | grep "python3 app.py"

# 后端日志
tail -f /tmp/rkllm_server.log  # 如果启动时重定向了日志
```

**重启服务：**
```bash
# 找到进程 PID
ps aux | grep "app.py"
# 杀死进程
kill <PID>
# 重新启动
python3 app.py
```

## 技术亮点

1. **清爽设计** - 使用 Tailwind CSS，无需额外 CSS 文件
2. **流式支持** - 完整实现 SSE 流式响应处理
3. **错误处理** - 全面的错误捕获和用户友好的提示
4. **无耦合** - 完全独立于后端，可单独更新维护
5. **易于扩展** - 清晰的代码结构，易于添加新功能

## 许可证

与 RKLLM 项目同级许可证

## 支持

遇到问题？检查：
1. 两个服务 (8000 和 8080) 是否都在运行
2. 运行 `test.py` 验证集成
3. 浏览器控制台看是否有 JavaScript 错误
4. 检查网络连接畅通
