"""
汽车销售智能体助理 - 主程序入口
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_deepseek import ChatDeepSeek
from agents.sales_agent import SalesGPT
from config.settings import (
    DEEPSEEK_API_KEY, 
    LLM_MODEL, 
    LLM_TEMPERATURE, 
    USE_TOOLS, 
    VERBOSE
)

def main():
    """主程序入口"""
    print("🚗 汽车销售智能体助理启动中...")
    
    # 检查API密钥
    if not DEEPSEEK_API_KEY:
        print("❌ 错误：未设置DEEPSEEK_API_KEY环境变量")
        print("请设置环境变量：export DEEPSEEK_API_KEY='your_api_key_here'")
        return
    
    # 初始化LLM
    print("🤖 初始化语言模型...")
    model = ChatDeepSeek(
        model=LLM_MODEL,
        api_key=DEEPSEEK_API_KEY,
        temperature=LLM_TEMPERATURE,
    )
    
    # 初始化销售智能体
    print("👨‍💼 初始化销售智能体...")
    sales_agent = SalesGPT.from_llm(
        model, 
        verbose=VERBOSE, 
        use_tools=USE_TOOLS
    )
    
    # 初始化对话
    sales_agent.seed_agent()
    
    print("✅ 系统初始化完成！")
    print("💬 开始对话（输入 'quit' 退出）：")
    print("-" * 50)
    
    # 交互式对话
    while True:
        try:
            user_input = input("用户: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            if not user_input:
                continue
            
            # 处理用户输入
            sales_agent.human_step(user_input)
            sales_agent.determine_conversation_stage()
            sales_agent.step()
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误：{e}")

if __name__ == "__main__":
    main() 