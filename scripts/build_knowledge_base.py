import os
import json
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置HuggingFace镜像
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

def build_knowledge_base():
    """构建知识库"""
    print("开始构建知识库...")
    
    # 1. 加载文档
    knowledge_base_dir = "knowledge_base"
    
    if not os.path.exists(knowledge_base_dir):
        print(f"知识库目录 {knowledge_base_dir} 不存在，创建示例文档...")
        create_sample_documents()
    
    # 2. 加载所有文档
    loader = DirectoryLoader(
        knowledge_base_dir,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    
    documents = loader.load()
    print(f"加载了 {len(documents)} 个文档")
    
    # 3. 分割文档
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    split_docs = text_splitter.split_documents(documents)
    print(f"分割成 {len(split_docs)} 个片段")
    
    # 4. 创建嵌入模型
    embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model,
        model_kwargs={"device": "cpu"}
    )
    
    print(f"使用嵌入模型: {embedding_model}")
    
    # 5. 创建向量数据库
    persist_directory = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    
    db = Chroma.from_documents(
        split_docs,
        embeddings,
        persist_directory=persist_directory,
        collection_name="claims_knowledge"
    )
    
    # 6. 持久化
    db.persist()
    
    print(f"知识库构建完成，存储在: {persist_directory}")
    print(f"向量数量: {db._collection.count()}")

def create_sample_documents():
    """创建示例文档"""
    sample_docs = {
        "车险/车险理赔流程.md": "# 车险理赔流程\n\n## 1. 报案\n- 发生事故后，立即拨打保险公司客服电话报案\n- 提供保单号、车牌号、事故时间地点等信息\n- 等待查勘员联系\n\n## 2. 现场查勘\n- 查勘员会到现场进行拍照定损\n- 确认事故责任和损失情况\n- 填写查勘报告\n\n## 3. 提交材料\n- 驾驶证、行驶证、身份证\n- 事故认定书\n- 维修发票\n- 其他相关证明\n\n## 4. 审核理赔\n- 保险公司审核材料\n- 确认理赔金额\n- 通知理赔结果\n\n## 5. 理赔支付\n- 审核通过后，保险公司支付理赔款\n- 一般3-5个工作日到账\n",
        "车险/车险理赔材料清单.md": "# 车险理赔材料清单\n\n## 基本材料\n1. **驾驶证**：原件及复印件\n2. **行驶证**：原件及复印件\n3. **身份证**：车主身份证原件及复印件\n4. **保险单**：原件\n\n## 事故相关材料\n1. **事故认定书**：交警出具的责任认定书\n2. **现场照片**：事故现场的照片\n3. **维修发票**：正规维修厂的发票\n4. **定损单**：保险公司出具的定损单\n\n## 特殊情况\n- **人伤案件**：需要医疗费用发票、病历、诊断证明\n- **物损案件**：需要财产损失证明\n- **盗抢案件**：需要报警记录、登报声明\n",
        "医疗险/医疗险理赔流程.md": "# 医疗险理赔流程\n\n## 1. 就医\n- 选择社保定点医院或保险公司指定医院\n- 保留所有医疗费用单据\n\n## 2. 报案\n- 出院后及时向保险公司报案\n- 提供保单号、身份证号等信息\n\n## 3. 提交材料\n- 医疗费用发票原件\n- 病历、诊断证明\n- 费用明细清单\n- 身份证复印件\n\n## 4. 审核\n- 保险公司审核材料\n- 确认理赔范围和金额\n\n## 5. 理赔支付\n- 审核通过后支付理赔款\n- 一般5-7个工作日到账\n",
        "财产险/财产险理赔流程.md": "# 财产险理赔流程\n\n## 1. 报案\n- 发现财产损失后立即报案\n- 提供保单号、损失情况等信息\n\n## 2. 现场查勘\n- 查勘员现场查勘损失情况\n- 拍照取证\n\n## 3. 提交材料\n- 财产损失清单\n- 购买凭证\n- 损失照片\n- 其他相关证明\n\n## 4. 定损核损\n- 评估损失金额\n- 确认理赔范围\n\n## 5. 理赔支付\n- 审核通过后支付理赔款\n",
        "意外险/意外险理赔流程.md": "# 意外险理赔流程\n\n## 1. 报案\n- 发生意外后及时报案\n- 提供保单号、身份证号等信息\n\n## 2. 就医治疗\n- 选择正规医院治疗\n- 保留所有医疗单据\n\n## 3. 提交材料\n- 医疗费用发票\n- 病历、诊断证明\n- 意外事故证明\n- 身份证复印件\n\n## 4. 审核\n- 保险公司审核材料\n- 确认是否属于保险责任\n\n## 5. 理赔支付\n- 审核通过后支付理赔款\n"
    }
    
    for path, content in sample_docs.items():
        full_path = os.path.join("knowledge_base", path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"创建示例文档: {full_path}")

if __name__ == "__main__":
    build_knowledge_base()
