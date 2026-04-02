from langchain_core.messages import HumanMessage
import json
import logging

logger = logging.getLogger(__name__)


class GuardrailsMiddleware:
    """对话守卫中间件，确保对话保持在理赔相关主题"""
    
    def __init__(self):
        # 理赔相关关键词
        self.claims_keywords = [
            "理赔", "保险", "保单", "车险", "医疗险", "财产险", "意外险",
            "理赔流程", "理赔材料", "理赔进度", "理赔申请", "理赔金额",
            "理赔时间", "理赔条件", "理赔范围", "理赔须知", "理赔案例",
            "保险条款", "投保", "续保", "退保", "保险责任"
        ]
        
        # 无关主题关键词
        self.irrelevant_keywords = [
            "聊天", "闲聊", "天气", "新闻", "娱乐", "体育", "游戏",
            "股票", "投资", "政治", "宗教", "色情", "暴力", "违法"
        ]
    
    async def _classify_query(self, messages):
        """
        分类用户查询，判断是否与理赔相关
        
        Args:
            messages: 消息列表
        
        Returns:
            "ALLOWED" 或 "DENIED"
        """
        try:
            # 获取最新的用户消息
            user_message = None
            for msg in reversed(messages):
                if isinstance(msg, HumanMessage):
                    user_message = msg.content
                    break
            
            if not user_message:
                return "ALLOWED"
            
            # 转换为小写
            text = user_message.lower()
            
            # 检查是否包含无关关键词
            for keyword in self.irrelevant_keywords:
                if keyword in text:
                    logger.info(f"检测到无关关键词: {keyword}")
                    return "DENIED"
            
            # 检查是否包含理赔相关关键词
            for keyword in self.claims_keywords:
                if keyword in text:
                    return "ALLOWED"
            
            # 对于没有明确理赔关键词的查询，进行更宽松的判断
            # 检查是否包含疑问词
            question_words = ["怎么", "如何", "什么", "哪里", "何时", "为什么", "怎样", "能否", "是否"]
            has_question = any(word in text for word in question_words)
            
            # 检查是否包含保险相关词汇
            insurance_related = any(word in text for word in ["保险", "理赔", "保单"])
            
            if has_question or insurance_related:
                return "ALLOWED"
            
            # 默认拒绝
            logger.info("查询与理赔无关，拒绝处理")
            return "DENIED"
            
        except Exception as e:
            logger.error(f"分类查询时出错: {e}")
            return "ALLOWED"  # 出错时默认允许
    
    async def check_relevance(self, query):
        """
        检查查询是否与理赔相关
        
        Args:
            query: 用户查询
        
        Returns:
            bool: 是否相关
        """
        messages = [HumanMessage(content=query)]
        result = await self._classify_query(messages)
        return result == "ALLOWED"
