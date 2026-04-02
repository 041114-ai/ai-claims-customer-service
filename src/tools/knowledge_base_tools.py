from langchain_community.vectorstores import Chroma
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
import os
import json
import logging

logger = logging.getLogger(__name__)

# 配置HuggingFace镜像
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 全局变量
_chroma_db = None


def get_chroma_db():
    """获取Chroma数据库实例"""
    global _chroma_db
    if _chroma_db is None:
        try:
            persist_directory = os.getenv("CHROMA_DB_PATH", "./chroma_db")
            embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            
            # 使用HuggingFace Embeddings
            embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                model_kwargs={"device": "cpu"}
            )
            
            _chroma_db = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
            )
            logger.info("Chroma DB loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Chroma DB: {e}")
            _chroma_db = None
    return _chroma_db


@tool

def search_knowledge_base(query: str, category: str = "all", k: int = 3) -> str:
    """
    搜索知识库
    
    Args:
        query: 搜索查询
        category: 分类（all, 车险, 医疗险, 财产险, 意外险）
        k: 返回结果数量
    
    Returns:
        JSON格式的搜索结果
    """
    try:
        db = get_chroma_db()
        
        if db is None:
            return json.dumps({
                "articles": [],
                "error": "知识库未初始化，请先运行构建脚本"
            }, ensure_ascii=False)
        
        # 搜索知识库
        results = db.similarity_search_with_score(query, k=k)
        
        articles = []
        for doc, score in results:
            # 检查文档是否有元数据
            if hasattr(doc, "metadata"):
                metadata = doc.metadata
            else:
                metadata = {}
            
            article = {
                "title": metadata.get("title", "未知标题"),
                "content": doc.page_content,
                "score": float(score),
                "category": metadata.get("category", "未分类"),
                "source": metadata.get("source", "知识库")
            }
            articles.append(article)
        
        # 如果指定了分类，过滤结果
        if category != "all":
            articles = [a for a in articles if a["category"] == category]
        
        return json.dumps({
            "articles": articles,
            "total": len(articles)
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"搜索知识库时出错: {e}")
        return json.dumps({
            "articles": [],
            "error": str(e)
        }, ensure_ascii=False)


@tool

def get_knowledge_categories() -> str:
    """
    获取知识库分类
    
    Returns:
        JSON格式的分类列表
    """
    try:
        db = get_chroma_db()
        
        if db is None:
            return json.dumps({
                "categories": [],
                "error": "知识库未初始化"
            }, ensure_ascii=False)
        
        # 获取所有文档的分类
        categories = set()
        docs = db.get()
        
        if "metadatas" in docs:
            for metadata in docs["metadatas"]:
                if isinstance(metadata, dict) and "category" in metadata:
                    categories.add(metadata["category"])
        
        return json.dumps({
            "categories": list(categories),
            "total": len(categories)
        }, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"获取分类时出错: {e}")
        return json.dumps({
            "categories": [],
            "error": str(e)
        }, ensure_ascii=False)
