# RAG 系统示例 - DeepSeek API

这是一个使用 LangChain、Chroma 向量数据库和 DeepSeek API 构建的 RAG（检索增强生成）系统示例。

## 功能特点

- 📁 自动加载文件夹中的文档（支持 .txt, .md 格式）
- 🔤 智能文本分块
- 🔗 使用 HuggingFace 嵌入模型生成向量
- 💾 Chroma 向量数据库持久化存储
- 🤖 集成 DeepSeek API 进行问答
- 🔍 支持开启/关闭 RAG 检索

## 项目结构

```
/workspace/
├── documents/              # 存放文档的文件夹
│   ├── sample1.txt        # 示例文档 1
│   └── sample2.txt        # 示例文档 2
├── rag_demo/
│   ├── rag_system.py      # RAG 系统主程序
│   ├── requirements.txt   # Python 依赖
│   ├── chroma_db/         # 向量数据库（运行后自动生成）
│   └── README.md          # 本文件
└── .env                   # 环境变量配置
```

## 安装步骤

### 1. 安装依赖

```bash
cd /workspace/rag_demo
pip install -r requirements.txt
```

如果磁盘空间有限，可以单独安装：

```bash
pip install --no-cache-dir langchain-core langchain-text-splitters chromadb sentence-transformers openai python-dotenv
```

### 2. 配置 API Key

编辑 `/workspace/.env` 文件，填入您的 DeepSeek API Key：

```
DEEPSEEK_API_KEY=sk-your-actual-api-key
```

您可以在 [DeepSeek 官网](https://platform.deepseek.com/) 获取 API Key。

### 3. 准备文档

将您的文档放入 `/workspace/documents/` 文件夹中，支持以下格式：
- `.txt` - 纯文本文件
- `.md` - Markdown 文件

### 4. 运行 RAG 系统

```bash
cd /workspace/rag_demo
python rag_system.py
```

## 使用方法

1. 启动程序后，系统会自动：
   - 加载 `documents` 文件夹中的所有文档
   - 将文档分割成适当的片段
   - 生成向量并存储到 Chroma 数据库

2. 输入问题进行提问，例如：
   - "DeepSeek 是做什么的？"
   - "什么是 RAG？"

3. 系统会询问是否使用 RAG 检索：
   - 输入 `Y`（默认）：使用 RAG，从文档中检索相关信息
   - 输入 `n`：不使用 RAG，直接调用 DeepSeek API

## 代码说明

### RAGSystem 类

主要方法：

- `__init__()`: 初始化系统，加载嵌入模型和向量数据库
- `_load_documents()`: 从文件夹加载文档
- `_init_vectorstore()`: 初始化或加载向量数据库
- `retrieve(query, k)`: 检索与查询最相关的 k 个文档片段
- `ask(question, use_rag, k)`: 回答问题，可选择是否使用 RAG

### 工作流程

1. **文档加载**: 读取文件夹中的所有文档
2. **文本分块**: 将长文档分割成适当大小的片段
3. **向量化**: 使用嵌入模型将文本转换为向量
4. **存储**: 将向量存储到 Chroma 数据库
5. **检索**: 根据用户问题检索相关文档片段
6. **生成**: 将检索到的上下文和问题发送给 DeepSeek API 生成回答

## 自定义配置

您可以在创建 RAGSystem 实例时调整以下参数：

```python
rag = RAGSystem(
    docs_folder="../documents",           # 文档文件夹路径
    persist_directory="./chroma_db",      # 向量数据库存储路径
    embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",  # 嵌入模型
    chunk_size=500,                       # 文本分块大小
    chunk_overlap=50                      # 分块重叠大小
)
```

## 常见问题

### Q: 如何添加更多文档？
A: 只需将新文档放入 `documents` 文件夹，然后删除 `chroma_db` 文件夹重新运行即可。

### Q: 可以使用其他嵌入模型吗？
A: 可以，修改 `embedding_model` 参数为任何 HuggingFace 支持的句子变换器模型。

### Q: 如何提高检索质量？
A: 可以尝试：
- 调整 `chunk_size` 和 `chunk_overlap` 参数
- 增加检索的文档数量 `k`
- 使用更高质量的嵌入模型

## 许可证

MIT License
