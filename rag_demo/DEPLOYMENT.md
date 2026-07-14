# 部署指南：如何打包和分发 RAG 应用

## 方案一：使用 Docker 镜像（推荐）

这是最干净、最通用的方式。所有依赖、Python 环境、甚至嵌入模型都打包在一个镜像里。

### 构建镜像
在 `rag_demo` 目录下运行：
```bash
docker build -t my-rag-app .
```
*注意：首次构建会自动下载 Python 依赖和 BAAI/bge-m3 模型，可能需要几分钟，构建完成后镜像大小约 2-3GB。*

### 运行容器
```bash
# 挂载本地 documents 文件夹和 .env 文件，方便修改文档和配置
docker run -it --rm \
  -v $(pwd)/../documents:/app/documents \
  -v $(pwd)/../.env:/app/.env \
  -v $(pwd)/chroma_db:/app/chroma_db \
  my-rag-app
```

**优点：**
- 环境完全隔离，不污染宿主机
- "一次构建，到处运行"
- 模型已预下载并固化在镜像中，启动秒开
- 适合部署到服务器或分享给团队成员

---

## 方案二：Portable Python (将 Python 环境安装到当前目录)

如果你不想用 Docker，可以将整个 Python 虚拟环境放在项目文件夹内，然后直接压缩整个文件夹分发给别人。

### 1. 创建虚拟环境到当前目录
在项目根目录执行：
```bash
# 创建一个名为 'venv' 的虚拟环境，路径就在当前文件夹下
python -m venv venv
```

### 2. 激活并安装依赖
**Windows:**
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 预下载模型到项目目录 (关键步骤)
代码已经配置为将模型下载到 `./.cache/huggingface` 目录。只需运行一次程序，模型就会自动下载到项目文件夹内：

```bash
# Windows
venv\Scripts\activate
python rag_system.py
# 输入一个测试问题后退出，模型已下载完成

# Linux/Mac
source venv/bin/activate
python rag_system.py
```

### 4. 如何分发给别人？

#### Windows 用户：
1. 直接压缩整个 `rag_demo` 文件夹（包含 `venv` 和 `.cache` 文件夹）
2. 发送给其他人
3. 接收者解压后，运行 `venv\Scripts\activate` 然后 `python rag_system.py`

> **注意**：虚拟环境有时对绝对路径敏感。如果跨机器运行有问题，接收者只需删除 `venv` 文件夹，重新执行步骤 1-3 即可（模型已在 `.cache` 中，无需重新下载）。

#### Linux/Mac 用户：
同上，使用 `source venv/bin/activate` 激活环境。

---

## 方案对比

| 特性 | Docker 镜像 | 虚拟环境打包 |
|------|------------|-------------|
| 易用性 | ⭐⭐⭐⭐⭐ (一条命令运行) | ⭐⭐⭐ (需激活环境) |
| 跨平台 | ⭐⭐⭐⭐⭐ | ⭐⭐ (需对应系统) |
| 文件大小 | 较大 (2-3GB) | 较大 (2-3GB) |
| 启动速度 | 秒开 | 秒开 |
| 适合场景 | 生产部署、团队协作 | 快速分享、离线演示 |

**建议**：优先使用 Docker，除非你有特殊需求。
