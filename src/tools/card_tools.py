from typing import Dict, Any, List
import re


def check_query_intent(query: str) -> Dict[str, Any]:
    """检查用户查询意图，判断是否需要显示卡片"""
    # 理赔进度查询关键词
    progress_keywords = [
        "理赔进度", "理赔状态", "我的理赔", "理赔怎么样了", "理赔到哪一步了",
        "理赔什么时候到", "理赔进展", "理赔处理", "理赔审核", "理赔流程"
    ]
    
    # 理赔入口查询关键词
    entry_keywords = [
        "怎么理赔", "如何理赔", "理赔入口", "理赔申请", "理赔方式",
        "理赔渠道", "哪里理赔", "开始理赔", "申请理赔", "理赔步骤"
    ]
    
    query_lower = query.lower()
    
    # 检查是否包含理赔进度关键词
    for keyword in progress_keywords:
        if keyword in query_lower:
            return {
                "show_card": True,
                "card_type": "progress",
                "response_text": "以下是您的理赔进度信息："
            }
    
    # 检查是否包含理赔入口关键词
    for keyword in entry_keywords:
        if keyword in query_lower:
            return {
                "show_card": True,
                "card_type": "entry",
                "response_text": "以下是理赔服务入口信息："
            }
    
    return {
        "show_card": False,
        "card_type": None,
        "response_text": None
    }


def generate_claim_progress_card() -> Dict[str, Any]:
    """生成理赔进度查询卡片数据"""
    # 模拟保单数据
    policies = [
        {
            "policy_no": "POL2024001",
            "policy_name": "平安车险",
            "claim_no": "CLM2024001001",
            "claim_type": "车险理赔",
            "status": "审核中",
            "status_code": "reviewing",
            "submit_date": "2024-03-15",
            "estimate_finish": "2024-03-22",
            "progress": 60,
            "current_step": "资料审核",
            "next_step": "现场勘查",
            "amount": "8500.00",
            "steps": [
                {"name": "提交申请", "status": "completed", "date": "2024-03-15"},
                {"name": "资料审核", "status": "in_progress", "date": "2024-03-16"},
                {"name": "现场勘查", "status": "pending", "date": None},
                {"name": "定损核算", "status": "pending", "date": None},
                {"name": "理赔支付", "status": "pending", "date": None},
            ]
        },
        {
            "policy_no": "POL2024002",
            "policy_name": "人保医疗险",
            "claim_no": "CLM2024002001",
            "claim_type": "医疗险理赔",
            "status": "已完成",
            "status_code": "completed",
            "submit_date": "2024-02-20",
            "estimate_finish": "2024-02-28",
            "progress": 100,
            "current_step": "理赔支付",
            "next_step": "完成",
            "amount": "3200.50",
            "steps": [
                {"name": "提交申请", "status": "completed", "date": "2024-02-20"},
                {"name": "资料审核", "status": "completed", "date": "2024-02-21"},
                {"name": "医疗审核", "status": "completed", "date": "2024-02-25"},
                {"name": "理赔核算", "status": "completed", "date": "2024-02-27"},
                {"name": "理赔支付", "status": "completed", "date": "2024-02-28"},
            ]
        },
        {
            "policy_no": "POL2024003",
            "policy_name": "太平洋财产险",
            "claim_no": "CLM2024003001",
            "claim_type": "财产险理赔",
            "status": "待补充材料",
            "status_code": "pending_docs",
            "submit_date": "2024-03-10",
            "estimate_finish": "2024-03-25",
            "progress": 30,
            "current_step": "资料审核",
            "next_step": "补充材料",
            "amount": "15000.00",
            "steps": [
                {"name": "提交申请", "status": "completed", "date": "2024-03-10"},
                {"name": "资料审核", "status": "in_progress", "date": "2024-03-12"},
                {"name": "现场勘查", "status": "pending", "date": None},
                {"name": "定损核算", "status": "pending", "date": None},
                {"name": "理赔支付", "status": "pending", "date": None},
            ]
        }
    ]
    
    return {
        "card_type": "claim_progress",
        "title": "理赔进度查询",
        "total_count": len(policies),
        "in_progress_count": sum(1 for p in policies if p["status_code"] not in ["completed", "rejected"]),
        "completed_count": sum(1 for p in policies if p["status_code"] == "completed"),
        "policies": policies
    }


def generate_claim_entry_card() -> Dict[str, Any]:
    """生成理赔入口查询卡片数据"""
    entries = [
        {
            "type": "online",
            "title": "在线理赔申请",
            "icon": "💻",
            "description": "通过官网或APP在线提交理赔申请",
            "channels": [
                {"name": "官方网站", "url": "https://claims.example.com/online", "icon": "🌐"},
                {"name": "手机APP", "url": "example://claims/apply", "icon": "📱"},
                {"name": "微信小程序", "url": "#", "icon": "💬"},
            ],
            "supported_types": ["车险", "医疗险", "意外险", "财产险"],
            "features": ["7×24小时", "实时进度查询", "电子材料上传"]
        },
        {
            "type": "offline",
            "title": "线下理赔服务",
            "icon": "🏢",
            "description": "前往保险公司营业网点办理理赔",
            "channels": [
                {"name": "营业网点", "url": "https://claims.example.com/branches", "icon": "📍"},
                {"name": "客服热线", "url": "tel:95518", "icon": "📞"},
            ],
            "supported_types": ["所有类型"],
            "features": ["面对面服务", "材料现场审核", "专人指导"]
        },
        {
            "type": "third_party",
            "title": "合作渠道",
            "icon": "🤝",
            "description": "通过合作机构办理理赔",
            "channels": [
                {"name": "合作医院", "url": "https://claims.example.com/hospitals", "icon": "🏥"},
                {"name": "汽车4S店", "url": "https://claims.example.com/dealers", "icon": "🚗"},
            ],
            "supported_types": ["医疗险", "车险"],
            "features": ["一站式服务", "快速处理", "绿色通道"]
        }
    ]
    
    quick_actions = [
        {"name": "上传理赔材料", "icon": "📤", "action": "upload_docs"},
        {"name": "查询理赔进度", "icon": "🔍", "action": "check_progress"},
        {"name": "预约查勘时间", "icon": "📅", "action": "schedule_survey"},
        {"name": "下载理赔单据", "icon": "📥", "action": "download_docs"},
    ]
    
    return {
        "card_type": "claim_entry",
        "title": "理赔服务入口",
        "entries": entries,
        "quick_actions": quick_actions
    }
