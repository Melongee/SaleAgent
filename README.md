---
title: 果猴手机销售助理
emoji: 📱
colorFrom: yellow
colorTo: blue
sdk: gradio
sdk_version: 5.35.0
app_file: app.py
pinned: false
short_description: Just for learning and fun.
---

# 手机销售智能体助理

一个基于LangChain和DeepSeek的手机销售助理系统，能够进行多轮对话，分析客户需求，并提供产品推荐。

## 功能特点

- 🤖 智能对话：基于销售流程的7阶段对话管理
- 📚 知识库：集成产品目录，提供准确的产品信息
- 🎯 需求分析：自动分析客户需求并推荐合适产品
- 💬 多轮对话：支持自然的多轮对话交互
- 🌐 Web界面：基于Gradio的友好用户界面

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 设置环境变量：
```bash
export DEEPSEEK_API_KEY="your_api_key_here"
```

3. 运行应用：
```bash
python sale_agent/app.py
```

## 配置说明

在 `config/settings.py` 中可以配置：
- LLM模型参数
- 销售代理信息
- 公司信息
- 对话阶段定义

## 使用说明

1. 启动应用后，在Web界面中输入消息
2. 系统会自动分析对话阶段并给出相应回复
3. 支持产品查询、需求分析、异议处理等功能
4. 对话会按照销售流程的7个阶段进行管理