import os
import re
from typing import Any, Callable, Dict, List, Union

from langchain.agents import AgentExecutor, LLMSingleActionAgent, Tool
from langchain.agents.agent import AgentOutputParser
from langchain.agents.conversational.prompt import FORMAT_INSTRUCTIONS
from langchain.chains import LLMChain, RetrievalQA
from langchain.chains.base import Chain
from langchain.prompts.base import StringPromptTemplate
from langchain_community.llms import BaseLLM
from langchain_community.vectorstores import Chroma
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.output_parsers.json import parse_json_markdown
from langchain_core.exceptions import OutputParserException
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from pydantic import BaseModel, Field

from chains.stage_analyzer import StageAnalyzerChain
from chains.sales_conversation import SalesConversationChain
from utils.prompts import get_sales_agent_tools_prompt
from config.settings import (
    EMBEDDINGS_PATH, 
    PRODUCT_CATALOG_FILE, 
    CONVERSATION_STAGES,
    SALES_AGENT_CONFIG
)


def setup_knowledge_base(product_catalog: str = None, llm=None):
    """建立知识库"""
    # load product catalog
    with open(product_catalog, "r", encoding="utf-8") as f:
        product_catalog = f.read()

    text_splitter = CharacterTextSplitter(chunk_size=10, chunk_overlap=0)
    texts = text_splitter.split_text(product_catalog)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_PATH)
    docsearch = Chroma.from_texts(
        texts, embeddings, collection_name="product-knowledge-base"
    )

    knowledge_base = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=docsearch.as_retriever()
    )
    return knowledge_base


def get_tools(product_catalog, llm):
    """获取工具列表"""
    knowledge_base = setup_knowledge_base(product_catalog, llm)
    tools = [
        Tool(
            name="ProductSearch",
            func=knowledge_base.run,
            description="当您需要回答有关问界汽车产品信息的问题，可以将问题发给这个问界产品知识库工具",
        )
    ]
    return tools


class CustomPromptTemplateForTools(StringPromptTemplate):
    """自定义提示模板"""
    template: str
    tools_getter: Callable

    def format(self, **kwargs) -> str:
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        kwargs["agent_scratchpad"] = thoughts
        tools = self.tools_getter(kwargs["input"])
        kwargs["tools"] = "\n".join(
            [f"{tool.name}: {tool.description}" for tool in tools]
        )
        kwargs["tool_names"] = ", ".join([tool.name for tool in tools])
        return self.template.format(**kwargs)


class SalesConvoOutputParser(AgentOutputParser):
    """销售对话输出解析器"""
    ai_prefix: str = "AI"
    verbose: bool = False

    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        if self.verbose:
            print("TEXT")
            print(text)
            print("-------")
        try:
            response = parse_json_markdown(text)
            if isinstance(response, list):
                response = response[0]
            if response["isNeedTools"] == "False":
                return AgentFinish({"output": response["output"]}, text)
            else:
                return AgentAction(
                    response["action"], response.get("action_input", {}), text
                )
        except Exception as e:
            raise OutputParserException(f"Could not parse LLM output: {text}") from e

    @property
    def _type(self) -> str:
        return "sales-agent"


class SalesGPT(Chain):
    """销售代理的控制器模型。"""

    conversation_history: List[str] = []
    current_conversation_stage: str = "1"
    stage_analyzer_chain: StageAnalyzerChain = Field(...)
    sales_conversation_utterance_chain: SalesConversationChain = Field(...)
    sales_agent_executor: Union[AgentExecutor, None] = Field(...)
    use_tools: bool = False

    conversation_stage_dict: Dict = CONVERSATION_STAGES

    # 销售代理配置
    salesperson_name: str = SALES_AGENT_CONFIG["salesperson_name"]
    salesperson_role: str = SALES_AGENT_CONFIG["salesperson_role"]
    company_name: str = SALES_AGENT_CONFIG["company_name"]
    company_business: str = SALES_AGENT_CONFIG["company_business"]
    company_values: str = SALES_AGENT_CONFIG["company_values"]
    conversation_purpose: str = SALES_AGENT_CONFIG["conversation_purpose"]
    conversation_type: str = SALES_AGENT_CONFIG["conversation_type"]

    def retrieve_conversation_stage(self, key):
        """获取对话阶段"""
        return self.conversation_stage_dict.get(str(key), self.conversation_stage_dict["1"])

    @property
    def input_keys(self) -> List[str]:
        return []

    @property
    def output_keys(self) -> List[str]:
        return []

    def seed_agent(self):
        """初始化智能体"""
        self.current_conversation_stage = self.retrieve_conversation_stage("1")
        self.conversation_history = []

    def determine_conversation_stage(self):
        """确定对话阶段"""
        if len(self.conversation_history) > 0:
            conversation_history = '"\n"'.join(self.conversation_history)
        else:
            conversation_history = '"\n暂无历史对话"'
        conversation_stage_id = self.stage_analyzer_chain.run(
            conversation_history=conversation_history,
            current_conversation_stage=self.current_conversation_stage,
        )

        self.current_conversation_stage = self.retrieve_conversation_stage(
            conversation_stage_id
        )

        print(f"Conversation Stage: {self.current_conversation_stage}")

    def human_step(self, human_input):
        """处理用户输入"""
        human_input = "User: " + human_input + " <END_OF_TURN>"
        self.conversation_history.append(human_input)

    def step(self):
        """执行一步对话"""
        self._call(inputs={})

    def _call(self, inputs: Dict[str, Any]) -> None:
        """运行销售代理的一步。"""
        if self.use_tools:
            ai_message = self.sales_agent_executor.run(
                input="",
                conversation_stage=self.current_conversation_stage,
                conversation_history="\n".join(self.conversation_history),
                salesperson_name=self.salesperson_name,
                salesperson_role=self.salesperson_role,
                company_name=self.company_name,
                company_business=self.company_business,
                company_values=self.company_values,
                conversation_purpose=self.conversation_purpose,
                conversation_type=self.conversation_type,
            )
        else:
            ai_message = self.sales_conversation_utterance_chain.run(
                salesperson_name=self.salesperson_name,
                salesperson_role=self.salesperson_role,
                company_name=self.company_name,
                company_business=self.company_business,
                company_values=self.company_values,
                conversation_purpose=self.conversation_purpose,
                conversation_history="\n".join(self.conversation_history),
                conversation_stage=self.current_conversation_stage,
                conversation_type=self.conversation_type,
            )

        print(f"{self.salesperson_name}: ", ai_message.rstrip("<END_OF_TURN>"))
        agent_name = self.salesperson_name
        ai_message = agent_name + ": " + ai_message
        if "<END_OF_TURN>" not in ai_message:
            ai_message += " <END_OF_TURN>"
        self.conversation_history.append(ai_message)

        return {}

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = False, **kwargs) -> "SalesGPT":
        """初始化 SalesGPT 控制器。"""
        stage_analyzer_chain = StageAnalyzerChain.from_llm(llm, verbose=verbose)
        sales_conversation_utterance_chain = SalesConversationChain.from_llm(
            llm, verbose=verbose
        )

        if "use_tools" in kwargs.keys() and kwargs["use_tools"] is False:
            sales_agent_executor = None
        else:
            product_catalog = kwargs.get("product_catalog", PRODUCT_CATALOG_FILE)
            tools = get_tools(product_catalog, llm)

            prompt = CustomPromptTemplateForTools(
                template=get_sales_agent_tools_prompt(),
                tools_getter=lambda x: tools,
                input_variables=[
                    "input",
                    "intermediate_steps",
                    "salesperson_name",
                    "salesperson_role",
                    "company_name",
                    "company_business",
                    "company_values",
                    "conversation_purpose",
                    "conversation_type",
                    "conversation_history",
                    "conversation_stage",
                ],
            )
            llm_chain = LLMChain(llm=llm, prompt=prompt, verbose=verbose)
            tool_names = [tool.name for tool in tools]
            output_parser = SalesConvoOutputParser(ai_prefix=kwargs.get("salesperson_name", "小陈"))

            sales_agent_with_tools = LLMSingleActionAgent(
                llm_chain=llm_chain,
                output_parser=output_parser,
                stop=["\nObservation:"],
                allowed_tools=tool_names,
                verbose=verbose,
            )

            sales_agent_executor = AgentExecutor.from_agent_and_tools(
                agent=sales_agent_with_tools, tools=tools, verbose=verbose
            )

        return cls(
            stage_analyzer_chain=stage_analyzer_chain,
            sales_conversation_utterance_chain=sales_conversation_utterance_chain,
            sales_agent_executor=sales_agent_executor,
            verbose=verbose,
            **kwargs,
        ) 