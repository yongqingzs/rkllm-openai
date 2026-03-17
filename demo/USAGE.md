# RKLLM Vision-Language Model Demo 使用指南

## 环境激活

```bash
conda activate llm_api1
cd /home/cat/llm/rkllm-openai
```

## 启动服务器

**终端 1:**
```bash
conda activate llm_api1
cd /home/cat/llm/rkllm-openai
python3 main.py
```

## 调用模型

### 1. 流式输出示例（推荐）

**终端 2:**

#### 使用默认参数
```bash
conda activate llm_api1
cd /home/cat/llm/rkllm-openai
python3 demo/example_vlm_stream.py
```

#### 自定义 prompt
```bash
python3 demo/example_vlm_stream.py --prompt "这张图片里有多少只长颈鹿？"
```

#### 自定义图片路径
```bash
python3 demo/example_vlm_stream.py \
  --image-path /home/cat/llm/rknn-llm/datasets/000000000025.jpg \
  --prompt "描述这张图片中的动物"
```

#### 自定义 API 地址
```bash
python3 demo/example_vlm_stream.py \
  --base-url http://localhost:8000/v1 \
  --api-key your-api-key
```

#### 查看所有选项
```bash
python3 demo/example_vlm_stream.py --help
```

**参数说明:**
- `--prompt TEXT` - 查询提示词（默认：这张图片是什么？用中文回答。）
- `--image-path PATH` - 图片文件路径（默认：/home/cat/llm/rknn-llm/datasets/000000000025.jpg）
- `--base-url URL` - API 服务地址（默认：http://localhost:8080/v1）
- `--api-key KEY` - API 密钥（默认：none）
- `--model NAME` - 模型名称（默认：rkllm-model）

---

### 2. 非流式输出示例

#### 使用默认参数
```bash
python3 demo/example_vlm.py
```

#### 自定义参数
```bash
python3 demo/example_vlm.py \
  --prompt "这张图片里的长颈鹿在做什么？" \
  --image-path /path/to/image.jpg
```

#### 查看所有选项
```bash
python3 demo/example_vlm.py --help
```

---

## 完整工作流示例

```bash
# 1. 激活环境
conda activate llm_api1
cd /home/cat/llm/rkllm-openai

# 2. 终端 1 - 启动服务器
python3 main.py

# 3. 终端 2 - 流式查询
python3 demo/example_vlm_stream.py --prompt "这是什么？"

# 4. 终端 2 - 非流式查询
python3 demo/example_vlm.py --prompt "图片中有什么？"
```

---

## 功能特性

### 流式输出 (`example_vlm_stream.py`)
- ✅ **实时流式输出** - 逐字符实时显示模型生成的内容
- ✅ **多项参数支持** - prompt、image-path、base-url、api-key、model
- ✅ **友好的进度提示** - 加载状态、连接状态、完成统计
- ✅ **错误处理** - 详细的错误提示和堆栈追踪
- ✅ **Token 统计** - 显示收到的 token 数量

### 非流式输出 (`example_vlm.py`)
- ✅ **一次性返回** - 等待完整回复后一次输出
- ✅ **相同的参数接口** - 与流式版本保持一致
- ✅ **详细的响应信息** - 显示 model ID、response ID 等

---

## 常见问题

**Q: 如何改变 API 服务地址？**
```bash
python3 demo/example_vlm_stream.py --base-url http://your-server:port/v1
```

**Q: 如何使用自己的图片？**
```bash
python3 demo/example_vlm_stream.py --image-path /path/to/your/image.jpg
```

**Q: 如何进行多轮对话？**
修改脚本中的 `messages` 参数，添加更多历史消息。

**Q: 流式输出和非流式输出有什么区别？**
- **流式** (`example_vlm_stream.py`): 实时看到模型逐字生成的内容，适合长回复
- **非流式** (`example_vlm.py`): 等待完整回复后一次显示，适合短回复或自动化脚本

---

## 测试状态

✅ 流式输出 - **通过** (50 tokens)  
✅ 自定义 prompt - **通过** (66 tokens)  
✅ 参数解析 - **通过** (help 正常显示)  
✅ 错误处理 - **通过** (文件不存在正确报错)  
✅ 非流式输出 - **通过** (完整回复返回)  
