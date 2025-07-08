import gradio as gr
from langchain_deepseek import ChatDeepSeek

from agents.sales_agent import SalesGPT
from config.settings import (
    DEEPSEEK_API_KEY, 
    LLM_MODEL, 
    LLM_TEMPERATURE, 
    USE_TOOLS,
    VERBOSE,
    GRADIO_TITLE,
    GRADIO_DESCRIPTION,
    SALES_AGENT_CONFIG
)

# 初始化LLM
model = ChatDeepSeek(
    model=LLM_MODEL,
    api_key=DEEPSEEK_API_KEY,
    temperature=LLM_TEMPERATURE,
)

# 初始化销售智能体
sales_agent = SalesGPT.from_llm(
    model, 
    verbose=VERBOSE, 
    use_tools=USE_TOOLS
)

# 初始化对话历史
chat_history = []

def add_user_message(user_message):
    """立即添加用户消息到聊天历史"""
    global chat_history
    chat_history.append({"role": "user", "content": user_message})
    return chat_history

def generate_ai_response(user_message):
    """生成AI回复"""
    global chat_history
    
    # 处理AI回复
    sales_agent.human_step(user_message)
    sales_agent.determine_conversation_stage()
    sales_agent.step()

    # 获取模型回复
    last_reply = sales_agent.conversation_history[-1].replace("<END_OF_TURN>", "").strip()

    # 添加AI回复
    chat_history.append({"role": "assistant", "content": last_reply})
    return chat_history

def clear_chat():
    """清空对话历史"""
    global chat_history
    chat_history = []
    sales_agent.seed_agent()
    return []

# 自定义CSS样式
custom_css = """
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    max-width: 98vw !important;
    width: 98vw !important;
    margin: 0 auto !important;
    padding: 0 !important;
}

.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    text-align: center;
}

/* 让主体横向分布 */
.flex-main {
    display: flex;
    flex-direction: row;
    gap: 2rem;
    width: 100%;
    justify-content: center;
    align-items: flex-start;
    margin-bottom: 2rem;
}

.chat-container {
    background: white;
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    flex: 2 1 0%;
    min-width: 400px;
    max-width: 900px;
    min-height: 600px;
    height: 70vh;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
}

.input-side {
    background: #f8f9fa;
    border-radius: 20px;
    padding: 1.5rem;
    border: 1px solid #e9ecef;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    flex: 1 1 0%;
    min-width: 320px;
    max-width: 400px;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    align-items: stretch;
}

.textbox-container {
    border-radius: 15px !important;
    border: 2px solid #e9ecef !important;
    transition: all 0.3s ease !important;
    background: white !important;
}

.textbox-container:focus-within {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

.chatbot-container {
    border-radius: 15px !important;
    border: 1px solid #e9ecef !important;
    background: #fafbfc !important;
    min-height: 500px !important;
    height: 100% !important;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 15px 30px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    color: white !important;
}

.btn-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
}

.btn-secondary {
    background: #6c757d !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 15px 30px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    color: white !important;
}

.btn-secondary:hover {
    background: #5a6268 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(108, 117, 125, 0.4) !important;
}

.footer {
    text-align: center;
    margin-top: 2rem;
    padding: 1.5rem;
    color: #6c757d;
    font-size: 0.9rem;
    background: #f8f9fa;
    border-radius: 15px;
    border: 1px solid #e9ecef;
}

.features {
    display: flex;
    justify-content: space-around;
    margin: 1rem 0;
    flex-wrap: wrap;
}

.feature-item {
    background: rgba(255,255,255,0.1);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    margin: 0.25rem;
    font-size: 0.9rem;
}
"""

# 创建Gradio界面
with gr.Blocks(title=GRADIO_TITLE, css=custom_css, theme=gr.themes.Soft()) as demo:
    # 主标题区域
    gr.HTML("""
        <div class="main-header">
            <h1>📱 果猴手机销售</h1>
            <p>专业的智能手机销售助手，为您提供个性化的建议和产品推荐</p>
            <div class="features">
                <span class="feature-item">🤖 智能对话</span>
                <span class="feature-item">📚 产品知识</span>
                <span class="feature-item">🎯 需求分析</span>
                <span class="feature-item">💡 专业建议</span>
            </div>
        </div>
    """)
    # 智能体信息
    gr.HTML(f"""
        <div class="agent-info">
            <strong>🤖 智能体信息</strong><br>
            销售顾问: {SALES_AGENT_CONFIG['salesperson_name']} | 
            公司: {SALES_AGENT_CONFIG['company_name']} | 
            专业领域: 手机销售
        </div>
    """)
    # 主体横向分布
    with gr.Row(elem_classes="flex-main"):
        with gr.Column(elem_classes="chat-container"):
            chatbot = gr.Chatbot(
                height=500,
                elem_classes="chatbot-container",
                type='messages',
                show_label=False
            )
        with gr.Column(elem_classes="input-side"):
            msg = gr.Textbox(
                label="💬 请输入您的问题",
                placeholder="例如：我想了解iPhone16的价格和配置，或者帮我推荐一款适合学生用的手机...",
                lines=3,
                max_lines=5,
                elem_classes="textbox-container"
            )
            submit_btn = gr.Button(
                "🚀 发送消息", 
                variant="primary",
                size="lg",
                elem_classes="btn-primary"
            )
            clear_btn = gr.Button(
                "🗑️ 清空对话", 
                variant="secondary",
                size="lg",
                elem_classes="btn-secondary"
            )
    # 页脚
    gr.HTML("""
        <div class="footer">
            <p><strong>💡 使用提示：</strong></p>
            <p>• 您可以询问产品信息、价格、配置、试驾安排等问题</p>
            <p>• 系统会根据您的需求自动推荐合适的车型</p>
            <p>• 支持多轮对话，可以深入讨论购车细节</p>
            <p><strong>🔒 隐私保护：</strong>您的对话信息仅用于提供更好的服务体验</p>
        </div>
    """)
    # 事件绑定
    msg.submit(add_user_message, inputs=msg, outputs=chatbot)
    msg.submit(lambda: "", None, msg)
    submit_btn.click(add_user_message, inputs=msg, outputs=chatbot)
    submit_btn.click(lambda: "", None, msg)
    msg.submit(generate_ai_response, inputs=msg, outputs=chatbot, queue=True)
    submit_btn.click(generate_ai_response, inputs=msg, outputs=chatbot, queue=True)
    clear_btn.click(clear_chat, outputs=chatbot)

if __name__ == "__main__":
    demo.launch(share=False, debug=True)