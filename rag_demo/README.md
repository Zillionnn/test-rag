# RAG 系统示例 - DeepSeek API

这个项目演示了如何构建一个完整的 RAG（检索增强生成）系统，能够：
1. 自动加载文件夹中的文档并建立向量索引
2. 使用本地嵌入模型进行向量化
3. 调用 DeepSeek API 进行智能问答
4. 支持持久化存储，无需重复处理文档

## 📁 项目结构

```
rag_demo/
├── rag_system.py      # 主程序
├── requirements.txt   # Python 依赖
├── Dockerfile         # Docker 镜像配置
├── DEPLOYMENT.md      # 部署指南
├── README.md          # 本文件
└── chroma_db/         # (运行后生成) 向量数据库
.cache/                # (运行后生成) 嵌入模型缓存
```

## 🚀 快速开始

### 方法一：使用 Docker（推荐）

```bash
# 1. 构建镜像（首次需要几分钟下载模型）
docker build -t my-rag-app .

# 2. 运行容器
docker run -it --rm \
  -v $(pwd)/../documents:/app/documents \
  -v $(pwd)/../.env:/app/.env \
  -v $(pwd)/chroma_db:/app/chroma_db \
  my-rag-app
```

### 方法二：本地 Python 环境

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
# 在项目根目录创建 .env 文件，填入你的 DeepSeek API Key

# 3. 运行程序
python rag_system.py
```

## ⚙️ 配置说明

### 1. 设置 DeepSeek API Key

在项目根目录（`/workspace`）创建 `.env` 文件：

```bash
DEEPSEEK_API_KEY=sk-your-api-key-here
```

### 2. 添加文档

将你的文档放入 `/workspace/documents/` 文件夹，支持格式：
- `.txt` - 纯文本文件
- `.md` - Markdown 文件

### 3. 自定义参数

可以在代码中调整以下参数：
- `embedding_model`: 嵌入模型（默认 `BAAI/bge-m3`，中文效果最佳）
- `chunk_size`: 文本分块大小（默认 500）
- `chunk_overlap`: 分块重叠（默认 50）

## 💡 使用说明

启动程序后：
1. 首次运行会自动处理文档并建立索引（耗时较长）
2. 后续运行直接加载已有索引（秒级启动）
3. 输入问题，选择是否使用 RAG 检索
4. 系统会返回基于文档的智能回答

## 🔧 高级功能

### 更换嵌入模型

编辑 `rag_system.py` 中的 `embedding_model` 参数：
```python
# 更高精度（推荐）
embedding_model="BAAI/bge-m3"

# 更快推理
embedding_model="BAAI/bge-large-zh-v1.5"
```

### 强制重新处理文档

删除 `chroma_db` 文件夹后重新运行：
```bash
rm -rf chroma_db
python rag_system.py
```

## 📦 打包分发

详见 [DEPLOYMENT.md](./DEPLOYMENT.md)，提供两种方案：
1. **Docker 镜像**：一次构建，到处运行
2. **虚拟环境打包**：将整个 Python 环境和模型下载到项目目录，压缩后直接分享

## 🎯 技术栈

- **LangChain**: RAG 流程编排
- **ChromaDB**: 轻量级向量数据库
- **HuggingFace Transformers**: 本地嵌入模型
- **DeepSeek API**: LLM 推理
- **SentenceTransformers**: 多语言文本嵌入

## ❓ 常见问题

**Q: 每次运行都要重新处理文档吗？**  
A: 不需要。向量数据库会持久化保存，只有文档变化时才会重新处理。

**Q: 嵌入模型需要下载吗？**  
A: 是的，首次运行会自动下载（约 1-2GB），之后使用本地缓存。代码已配置为下载到项目内的 `.cache` 目录，方便打包分发。

**Q: 哪个模型最精确？**  
A: 对于中文场景，推荐使用 `BAAI/bge-m3`，在 MTEB 评测中表现优异。

---

**作者**: AI Assistant  
**许可证**: MIT
