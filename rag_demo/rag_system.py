"""
RAG 系统示例 - 使用 DeepSeek API
功能：将文件夹中的文档构建为 RAG 系统，并调用 DeepSeek API 进行问答
"""

import os
import glob
from typing import List, Optional
from dotenv import load_dotenv

# LangChain 核心组件
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from openai import OpenAI

# 加载环境变量
load_dotenv()


class RAGSystem:
    """RAG 系统类，负责文档处理、检索和问答"""
    
    def __init__(
        self,
        docs_folder: str = "../documents",
        persist_directory: str = "./chroma_db",
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        chunk_size: int = 400,
        chunk_overlap: int = 40
    ):
        """
        初始化 RAG 系统
        
        Args:
            docs_folder: 文档文件夹路径
            persist_directory: 向量数据库持久化目录
            embedding_model: 嵌入模型名称
            chunk_size: 文本分块大小
            chunk_overlap: 分块重叠大小
        """
        self.docs_folder = docs_folder
        self.persist_directory = persist_directory
        
        # 初始化 DeepSeek 客户端
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("请在 .env 文件中设置 DEEPSEEK_API_KEY")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", ".", " ", ""]
        )
        
        # 初始化嵌入模型
        print("正在加载嵌入模型...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        
        # 初始化或加载向量数据库
        self.vectorstore = None
        self._init_vectorstore()
    
    def _load_documents(self) -> List[Document]:
        """从文件夹加载所有文档"""
        documents = []
        
        # 支持多种文件格式
        file_patterns = ["*.txt", "*.md", "*.pdf"]
        
        for pattern in file_patterns:
            file_paths = glob.glob(os.path.join(self.docs_folder, "**", pattern), recursive=True)
            
            for file_path in file_paths:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": os.path.basename(file_path),
                            "path": file_path
                        }
                    )
                    documents.append(doc)
                    print(f"已加载文档：{os.path.basename(file_path)}")
                    
                except Exception as e:
                    print(f"加载文档 {file_path} 失败：{e}")
        
        return documents
    
    def _init_vectorstore(self):
        """初始化向量数据库"""
        # 检查是否存在已保存的向量数据库
        if os.path.exists(self.persist_directory):
            print("加载已存在的向量数据库...")
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            # 创建新的向量数据库
            print("创建新的向量数据库...")
            documents = self._load_documents()
            
            if not documents:
                print("警告：未找到任何文档")
                return
            
            # 分割文档
            splits = self.text_splitter.split_documents(documents)
            print(f"文档已分割为 {len(splits)} 个片段")
            
            # 创建向量数据库
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            print("向量数据库创建完成")
    
    def retrieve(self, query: str, k: int = 3) -> List[str]:
        """
        检索相关文档片段
        
        Args:
            query: 查询文本
            k: 返回的相关片段数量
            
        Returns:
            相关文档片段列表
        """
        if not self.vectorstore:
            return []
        
        docs = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]
    
    def ask(self, question: str, use_rag: bool = True, k: int = 3) -> str:
        """
        回答问题
        
        Args:
            question: 用户问题
            use_rag: 是否使用 RAG
            k: 检索的文档片段数量
            
        Returns:
            AI 生成的回答
        """
        context = ""
        
        if use_rag and self.vectorstore:
            # 检索相关文档
            retrieved_docs = self.retrieve(question, k=k)
            
            if retrieved_docs:
                # 构建上下文
                context = "\n\n".join([
                    f"[相关文档 {i+1}]:\n{doc}" 
                    for i, doc in enumerate(retrieved_docs)
                ])
                print(f"\n检索到 {len(retrieved_docs)} 个相关文档片段")
        
        # 构建提示词
        if context:
            prompt = f"""基于以下参考信息回答问题。如果参考信息与问题无关，请根据你的知识回答。

参考信息：
{context}

问题：{question}

请用中文回答："""
        else:
            prompt = f"请用中文回答以下问题：{question}"
        
        # 调用 DeepSeek API
        print("\n正在调用 DeepSeek API...")
        try:
            response = self.client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": "你是一个有帮助的 AI 助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                reasoning_effort="high",
                extra_body={"thinking": {"type": "enabled"}},
            )
            
            answer = response.choices[0].message.content
            return answer
            
        except Exception as e:
            return f"调用 DeepSeek API 失败：{e}"


def main():
    """主函数 - 交互式问答"""
    print("=" * 60)
    print("RAG 系统 - DeepSeek 问答演示")
    print("=" * 60)
    
    # 初始化 RAG 系统
    try:
        rag = RAGSystem(
            docs_folder="../documents",
            persist_directory="./chroma_db"
        )
    except ValueError as e:
        print(f"错误：{e}")
        print("\n请在项目根目录创建 .env 文件，并添加以下内容：")
        print("DEEPSEEK_API_KEY=your_api_key_here")
        return
    
    print("\n系统初始化完成！")
    print("输入问题开始提问（输入 'quit' 退出）")
    print("-" * 60)
    
    while True:
        try:
            question = input("\n请输入问题：").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break
            
            if not question:
                continue
            
            # 选择是否使用 RAG
            use_rag_input = input("使用 RAG 检索？(Y/n): ").strip().lower()
            use_rag = use_rag_input != 'n'
            
            # 获取回答
            answer = rag.ask(question, use_rag=use_rag)
            
            print("\n" + "=" * 60)
            print("回答:")
            print("=" * 60)
            print(answer)
            print("=" * 60)
            
        except KeyboardInterrupt:
            print("\n\n程序中断，再见！")
            break
        except Exception as e:
            print(f"发生错误：{e}")


if __name__ == "__main__":
    main()
