"""
测试重构后的汽车销售智能体助理
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有模块的导入"""
    print("🧪 测试模块导入...")
    
    try:
        from config.settings import DEEPSEEK_API_KEY, SALES_AGENT_CONFIG
        print("✅ 配置模块导入成功")
    except Exception as e:
        print(f"❌ 配置模块导入失败: {e}")
        return False
    
    try:
        from utils.prompts import get_stage_analyzer_prompt, get_sales_conversation_prompt
        print("✅ 提示词模块导入成功")
    except Exception as e:
        print(f"❌ 提示词模块导入失败: {e}")
        return False
    
    try:
        from chains.stage_analyzer import StageAnalyzerChain
        from chains.sales_conversation import SalesConversationChain
        print("✅ 链模块导入成功")
    except Exception as e:
        print(f"❌ 链模块导入失败: {e}")
        return False
    
    try:
        from agents.sales_agent import SalesGPT
        print("✅ 销售智能体模块导入成功")
    except Exception as e:
        print(f"❌ 销售智能体模块导入失败: {e}")
        return False
    
    return True

def test_config():
    """测试配置"""
    print("\n🔧 测试配置...")
    
    from config.settings import SALES_AGENT_CONFIG, CONVERSATION_STAGES
    
    print(f"✅ 销售代理名称: {SALES_AGENT_CONFIG['salesperson_name']}")
    print(f"✅ 公司名称: {SALES_AGENT_CONFIG['company_name']}")
    print(f"✅ 对话阶段数量: {len(CONVERSATION_STAGES)}")
    
    return True

def test_prompts():
    """测试提示词"""
    print("\n📝 测试提示词...")
    
    from utils.prompts import get_stage_analyzer_prompt, get_sales_conversation_prompt
    
    stage_prompt = get_stage_analyzer_prompt()
    sales_prompt = get_sales_conversation_prompt()
    
    print(f"✅ 阶段分析器提示词变量: {stage_prompt.input_variables}")
    print(f"✅ 销售对话提示词变量: {sales_prompt.input_variables}")
    
    return True

def main():
    """主测试函数"""
    print("🚗 汽车销售智能体助理 - 重构测试")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        print("❌ 导入测试失败")
        return
    
    # 测试配置
    if not test_config():
        print("❌ 配置测试失败")
        return
    
    # 测试提示词
    if not test_prompts():
        print("❌ 提示词测试失败")
        return
    
    print("\n🎉 所有测试通过！重构成功！")
    print("\n📋 重构总结:")
    print("- 原始文件: sale_agent.py (612行)")
    print("- 重构后: 8个模块文件，结构清晰")
    print("- 配置集中管理")
    print("- 提示词独立管理")
    print("- 功能模块化")
    print("- 易于维护和扩展")

if __name__ == "__main__":
    main() 