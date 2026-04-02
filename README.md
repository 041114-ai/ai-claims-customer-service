# AI理赔智能客服系统

基于DeepSeek API和Chroma向量数据库的智能理赔客服系统，支持流式输出和智能卡片展示。

## 功能特性

- 🤖 **智能对话**：基于DeepSeek API的自然语言处理
- 📚 **知识库**：Chroma向量数据库存储理赔相关知识
- 🔍 **智能查询**：支持理赔进度和入口查询
- 📱 **现代化UI**：响应式设计，美观的卡片展示
- ⚡ **流式输出**：实时显示AI回复
- 🛡️ **对话守卫**：确保对话保持在理赔相关主题

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 文件为 `.env` 并填入你的 API Key：

```bash
cp .env.example .env
# 编辑 .env 文件，填入 DEEPSEEK_API_KEY
```

### 3. 构建知识库

```bash
python scripts/build_knowledge_base.py
```

### 4. 启动服务

```bash
python -m streamlit run app.py
```

## 目录结构

```
ai-claims-customer-service/
├── app.py                  # 主前端应用
├── src/
│   ├── agent/              # 智能体实现
│   ├── tools/              # 工具函数
│   ├── middleware/         # 中间件
│   └── prompts/            # 提示词模板
├── scripts/                # 脚本工具
│   └── build_knowledge_base.py  # 构建知识库
├── knowledge_base/         # 知识库文档
├── pyproject.toml          # 项目配置
├── .env.example            # 环境变量示例
└── README.md               # 项目说明
```

## 支持的理赔类型

- 🚗 车险理赔
- 🏥 医疗险理赔
- 🏠 财产险理赔
- ⚡ 意外险理赔

## 快捷查询

- 输入"理赔进度"查看状态
- 输入"怎么理赔"获取入口
- 输入具体理赔问题获取专业解答

## 技术栈

- **前端**：Streamlit
- **LLM**：DeepSeek API
- **向量数据库**：Chroma
- **嵌入模型**：HuggingFace Sentence Transformers
- **知识管理**：LangChain

## 注意事项

- 本系统仅提供理赔咨询服务，具体理赔事宜请以保险公司官方回复为准
- 首次运行时会下载嵌入模型，可能需要较长时间
- 请确保网络连接正常，以获取最佳体验
