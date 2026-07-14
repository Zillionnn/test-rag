# 基础镜像：使用 Python 3.10 slim 版本减小体积
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
# 1. 防止 Python 生成 .pyc 文件
# 2. 确保输出实时打印
# 3. 指定 HuggingFace 模型缓存目录到当前文件夹，方便持久化或加速构建
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface

# 安装系统级依赖 (chromadb 和 sentence-transformers 需要编译工具)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
# 先复制 requirements.txt 利用 Docker 缓存层，避免每次代码变动都重装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 【关键步骤】预下载嵌入模型
# 这样在构建镜像时就会下载模型，用户运行容器时无需等待下载
# 注意：这会增加镜像大小 (约 1-2GB)，但换取了启动速度
RUN python -c "from sentence_transformers import SentenceTransformer; print('正在下载模型...'); SentenceTransformer('BAAI/bge-m3'); print('模型下载完成')"

# 创建数据持久化目录 (可选，用于保存 ChromaDB 数据)
RUN mkdir -p /app/chroma_db

# 暴露端口 (如果需要作为 API 服务运行，目前示例是命令行交互，此步骤可选)
# EXPOSE 8000

# 默认启动命令
CMD ["python", "rag_system.py"]
