from openai import OpenAI
import os
import json

from src.tools.knowledge_base_tools import search_knowledge_base
from src.tools.card_tools import (
    generate_claim_progress_card, 
    generate_claim_entry_card, 
    check_query_intent
)
from src.middleware.guardrails_middleware import GuardrailsMiddleware
from src.prompts.claims_agent_prompt import CLAIMS_AGENT_PROMPT

import logging

logger = logging.getLogger(__name__)

_guardrails = GuardrailsMiddleware()
_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = "https://api.deepseek.com/v1" if os.getenv("DEEPSEEK_API_KEY") else None
        _client = OpenAI(api_key=api_key, base_url=base_url)
    return _client


async def chat(query: str, thread_id: str = "default"):
    from langchain_core.messages import HumanMessage
    
    messages = [HumanMessage(content=query)]
    
    is_allowed = await _guardrails._classify_query(messages)
    
    if is_allowed == "DENIED":
        yield "抱歉，我只能回答保险理赔相关的问题。如果您有理赔方面的疑问，请随时提问！"
        return
    
    try:
        client = get_client()
        
        # 检查用户意图，判断是否需要显示卡片
        intent_result = check_query_intent(query)
        
        # 如果需要显示卡片，先返回卡片数据
        if intent_result["show_card"]:
            card_data = None
            if intent_result["card_type"] == "progress":
                card_data = generate_claim_progress_card()
            elif intent_result["card_type"] == "entry":
                card_data = generate_claim_entry_card()
            
            if card_data:
                # 返回卡片标记，前端会解析并显示
                card_marker = f"[[CARD:{json.dumps(card_data, ensure_ascii=False)}]]"
                yield card_marker
        
        # 继续获取知识库信息和AI回复
        kb_result = search_knowledge_base.invoke({"query": query, "category": "all", "k": 3})
        
        try:
            kb_data = json.loads(kb_result)
            articles = kb_data.get("articles", [])
            
            if articles:
                context = "\n\n".join([
                    f"【{a['title']}】\n{a['content']}"
                    for a in articles
                ])
                
                system_prompt = f"""{CLAIMS_AGENT_PROMPT}

以下是知识库中的相关信息：

{context}

请基于以上信息回答用户的问题。如果知识库中没有相关信息，请坦诚告知。"""
            else:
                system_prompt = CLAIMS_AGENT_PROMPT
        except:
            system_prompt = CLAIMS_AGENT_PROMPT
        
        # 如果有卡片，在回复前加上提示
        if intent_result["show_card"] and intent_result["response_text"]:
            yield f"{intent_result['response_text']}\n\n"
        
        # 使用流式API
        stream = client.chat.completions.create(
            model="deepseek-chat" if os.getenv("DEEPSEEK_API_KEY") else "gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            temperature=0,
            stream=True,
        )
        
        # 流式输出
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
        
    except Exception as e:
        logger.error(f"Agent error: {e}")
        yield f"抱歉，系统出现错误：{str(e)}\n\n请稍后再试或联系人工客服。"


if __name__ == "__main__":
    import asyncio
    
    async def main():
        test_queries = [
            "我的理赔进度怎么样了？",
            "怎么申请车险理赔？",
            "车险理赔需要哪些材料？",
        ]
        
        for query in test_queries:
            print(f"\n用户: {query}")
            print("助手: ", end="", flush=True)
            async for response in chat(query):
                print(response, end="", flush=True)
            print("\n" + "="*50)
    
    asyncio.run(main())
