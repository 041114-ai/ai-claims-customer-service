import streamlit as st
from src.agent.claims_graph import chat
from langchain_core.messages import HumanMessage, AIMessage
import asyncio
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI京小赔",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 42px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 30px;
        letter-spacing: -0.5px;
    }
    
    .chat-container {
        background: white;
        border-radius: 24px;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 20px 20px 4px 20px;
        margin: 12px 0;
        margin-left: auto;
        max-width: 70%;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        animation: slideInRight 0.3s ease-out;
    }
    
    .assistant-message {
        background: #f8f9fa;
        color: #2d3748;
        padding: 16px 20px;
        border-radius: 20px 20px 20px 4px;
        margin: 12px 0;
        max-width: 70%;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        animation: slideInLeft 0.3s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .claim-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 24px;
        padding: 28px;
        margin: 20px 0;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        animation: fadeInUp 0.5s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .claim-card-title {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .claim-card-stats {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .claim-stat-item {
        background: rgba(255,255,255,0.25);
        backdrop-filter: blur(10px);
        padding: 16px;
        border-radius: 16px;
        text-align: center;
        transition: transform 0.2s;
    }
    
    .claim-stat-item:hover {
        transform: translateY(-2px);
    }
    
    .claim-stat-value {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .claim-stat-label {
        font-size: 13px;
        opacity: 0.95;
        font-weight: 500;
    }
    
    .policy-card {
        background: white;
        border-radius: 20px;
        padding: 24px;
        margin: 16px 0;
        color: #2d3748;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .policy-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .policy-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    
    .policy-name {
        font-weight: 700;
        font-size: 18px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .policy-status {
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    
    .status-reviewing {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        color: #6c5ce7;
    }
    
    .status-pending {
        background: linear-gradient(135deg, #fab1a0 0%, #e17055 100%);
        color: #d63031;
    }
    
    .status-completed {
        background: linear-gradient(135deg, #55efc4 0%, #00b894 100%);
        color: #00695c;
    }
    
    .progress-bar {
        background: #e9ecef;
        border-radius: 12px;
        height: 10px;
        margin: 16px 0;
        overflow: hidden;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        border-radius: 12px;
        transition: width 0.6s ease;
    }
    
    .policy-info {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        font-size: 14px;
        color: #64748b;
        margin-top: 16px;
    }
    
    .policy-info-item {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .timeline {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
        position: relative;
        padding: 0 10px;
    }
    
    .timeline::before {
        content: '';
        position: absolute;
        top: 20px;
        left: 30px;
        right: 30px;
        height: 3px;
        background: linear-gradient(90deg, #e9ecef 0%, #e9ecef 100%);
        z-index: 0;
        border-radius: 2px;
    }
    
    .timeline-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        z-index: 1;
        flex: 1;
    }
    
    .step-dot {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-bottom: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .step-completed {
        background: linear-gradient(135deg, #55efc4 0%, #00b894 100%);
        color: white;
    }
    
    .step-in-progress {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        color: white;
        animation: pulse 2s infinite;
    }
    
    .step-pending {
        background: #e9ecef;
        color: #adb5bd;
    }
    
    @keyframes pulse {
        0%, 100% { 
            transform: scale(1);
            box-shadow: 0 2px 8px rgba(253, 203, 110, 0.3);
        }
        50% { 
            transform: scale(1.1);
            box-shadow: 0 4px 16px rgba(253, 203, 110, 0.5);
        }
    }
    
    .step-name {
        font-size: 12px;
        color: #64748b;
        text-align: center;
        font-weight: 500;
    }
    
    .entry-card {
        background: white;
        border-radius: 20px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 5px solid;
        border-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%) 1;
        transition: all 0.3s ease;
    }
    
    .entry-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .entry-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }
    
    .entry-icon {
        font-size: 32px;
    }
    
    .entry-title {
        font-size: 20px;
        font-weight: 700;
        color: #2d3748;
    }
    
    .entry-desc {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 16px;
        line-height: 1.6;
    }
    
    .entry-channels {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 16px 0;
    }
    
    .entry-channel {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 6px;
        transition: all 0.2s;
        cursor: pointer;
    }
    
    .entry-channel:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transform: translateY(-2px);
    }
    
    .entry-features {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 16px;
    }
    
    .entry-feature {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        color: #667eea;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
    }
    
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        margin: 20px 0;
    }
    
    .quick-action-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 16px;
        border-radius: 16px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-size: 15px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .quick-action-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 24px;
        border-radius: 20px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .sidebar-title {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    .sidebar-subtitle {
        font-size: 13px;
        opacity: 0.9;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stChatInput > div > div {
        border-radius: 16px;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .stChatInput > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    @media (max-width: 768px) {
        .claim-card-stats {
            grid-template-columns: 1fr;
        }
        
        .quick-actions {
            grid-template-columns: 1fr;
        }
        
        .policy-info {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

def render_progress_card(card_data):
    """渲染理赔进度卡片"""
    policies = card_data.get("policies", [])
    total = card_data.get("total_count", 0)
    in_progress = card_data.get("in_progress_count", 0)
    completed = card_data.get("completed_count", 0)
    
    html = f"""
    <div class="claim-card">
        <div class="claim-card-title">
            📊 {card_data.get('title', '理赔进度查询')}
        </div>
        <div class="claim-card-stats">
            <div class="claim-stat-item">
                <div class="claim-stat-value">{total}</div>
                <div class="claim-stat-label">总保单</div>
            </div>
            <div class="claim-stat-item">
                <div class="claim-stat-value">{in_progress}</div>
                <div class="claim-stat-label">处理中</div>
            </div>
            <div class="claim-stat-item">
                <div class="claim-stat-value">{completed}</div>
                <div class="claim-stat-label">已完成</div>
            </div>
        </div>
    </div>
    """
    
    for policy in policies:
        status_class = {
            "reviewing": "status-reviewing",
            "pending_docs": "status-pending",
            "completed": "status-completed"
        }.get(policy.get("status_code"), "status-reviewing")
        
        progress = policy.get("progress", 0)
        
        steps_html = ""
        steps = policy.get("steps", [])
        for step in steps:
            step_status = step.get("status", "pending")
            step_class = {
                "completed": "step-completed ✓",
                "in_progress": "step-in-progress ●",
                "pending": "step-pending ○"
            }.get(step_status, "step-pending ○")
            
            steps_html += f"""
                <div class="timeline-step">
                    <div class="step-dot {step_class.split()[0]}">{step_class.split()[1] if len(step_class.split()) > 1 else ''}</div>
                    <div class="step-name">{step.get('name', '')}</div>
                </div>
            """
        
        html += f"""
        <div class="policy-card">
            <div class="policy-header">
                <span class="policy-name">{policy.get('policy_name', '')}</span>
                <span class="policy-status {status_class}">{policy.get('status', '')}</span>
            </div>
            <div style="font-size: 14px; color: #64748b; margin-bottom: 12px;">
                理赔单号: {policy.get('claim_no', '')}
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%"></div>
            </div>
            <div style="text-align: center; font-size: 14px; font-weight: 600; color: #667eea; margin-bottom: 16px;">
                进度: {progress}%
            </div>
            <div class="timeline">
                {steps_html}
            </div>
            <div class="policy-info">
                <div class="policy-info-item">💰 理赔金额: ¥{policy.get('amount', '0.00')}</div>
                <div class="policy-info-item">📅 申请日期: {policy.get('submit_date', '')}</div>
                <div class="policy-info-item">📋 当前步骤: {policy.get('current_step', '')}</div>
                <div class="policy-info-item">⏱️ 预计完成: {policy.get('estimate_finish', '')}</div>
            </div>
        </div>
        """
    
    return html

def render_entry_card(card_data):
    """渲染理赔入口卡片"""
    entries = card_data.get("entries", [])
    quick_actions = card_data.get("quick_actions", [])
    
    html = f"""
    <div class="claim-card">
        <div class="claim-card-title">
            🚪 {card_data.get('title', '理赔服务入口')}
        </div>
    </div>
    """
    
    if quick_actions:
        html += '<div class="quick-actions">'
        for action in quick_actions:
            html += f"""
                <button class="quick-action-btn">
                    <span>{action.get('icon', '')}</span>
                    <span>{action.get('name', '')}</span>
                </button>
            """
        html += '</div>'
    
    for entry in entries:
        channels_html = ""
        for channel in entry.get("channels", []):
            value = channel.get("value", channel.get("name", ""))
            icon = channel.get("icon", "")
            channels_html += f"""
                <div class="entry-channel">
                    <span>{icon}</span>
                    <span>{value}</span>
                </div>
            """
        
        features_html = ""
        for feature in entry.get("features", []):
            features_html += f'<span class="entry-feature">{feature}</span>'
        
        html += f"""
        <div class="entry-card">
            <div class="entry-header">
                <span class="entry-icon">{entry.get('icon', '')}</span>
                <span class="entry-title">{entry.get('title', '')}</span>
            </div>
            <div class="entry-desc">{entry.get('description', '')}</div>
            <div class="entry-channels">
                {channels_html}
            </div>
            <div class="entry-features">
                {features_html}
            </div>
        </div>
        """
    
    return html

def parse_and_render_cards(response_text):
    """解析并渲染卡片，返回清理后的文本"""
    card_pattern = r'\[\[CARD:(.*?)\]\]'
    match = re.search(card_pattern, response_text, re.DOTALL)
    
    if match:
        try:
            card_json = match.group(1)
            card_data = json.loads(card_json)
            
            clean_text = re.sub(card_pattern, '', response_text, flags=re.DOTALL).strip()
            
            card_type = card_data.get("card_type")
            if card_type == "claim_progress":
                card_html = render_progress_card(card_data)
                st.markdown(card_html, unsafe_allow_html=True)
            elif card_type == "claim_entry":
                card_html = render_entry_card(card_data)
                st.markdown(card_html, unsafe_allow_html=True)
            
            return clean_text
        except Exception as e:
            print(f"卡片渲染错误: {e}")
            return response_text
    
    return response_text

if "messages" not in st.session_state:
    st.session_state.messages = []

if "initialized" not in st.session_state:
    with st.spinner("正在初始化AI客服..."):
        st.session_state.initialized = True

st.markdown('<h1 class="main-title">🛡️ AI理赔智能客服</h1>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-title">📋 使用说明</div>
        <div class="sidebar-subtitle">智能理赔咨询服务</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 🎯 我可以帮您：
    - 🔍 解答理赔流程问题
    - 📝 指导准备理赔材料
    - ⏱️ 查询理赔进度
    - 💡 解决常见理赔问题
    - 📖 解释保险条款
    
    ### 📦 理赔类型：
    - 🚗 车险理赔
    - 🏥 医疗险理赔
    - 🏠 财产险理赔
    - ⚡ 意外险理赔
    
    ### ⚡ 快捷查询：
    - 输入"理赔进度"查看状态
    - 输入"怎么理赔"获取入口
    """)
    
    st.markdown("---")
    
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #64748b; font-size: 12px; padding: 10px;'>
        Powered by DeepSeek + Chroma
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        clean_content = parse_and_render_cards(message["content"])
        if clean_content:
            st.markdown(f'<div class="assistant-message">{clean_content}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

if prompt := st.chat_input("请输入您的理赔问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)
    
    message_placeholder = st.empty()
    full_response = ""
    
    try:
        async def stream_response():
            nonlocal full_response
            async for chunk in chat(prompt, thread_id="streamlit_user"):
                full_response += chunk
                # 实时更新显示
                clean_text = parse_and_render_cards(full_response)
                if clean_text:
                    message_placeholder.markdown(
                        f'<div class="assistant-message">{clean_text}</div>',
                        unsafe_allow_html=True
                    )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(stream_response())
        loop.close()
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        error_msg = f"抱歉，系统出现错误：{str(e)}\n\n请稍后再试或联系人工客服。"
        st.markdown(f'<div class="assistant-message">{error_msg}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.markdown("""
<div style='text-align: center; color: #64748b; font-size: 14px; padding: 20px;'>
    💡 提示：本系统仅提供理赔咨询服务，具体理赔事宜请以保险公司官方回复为准
</div>
""", unsafe_allow_html=True)
