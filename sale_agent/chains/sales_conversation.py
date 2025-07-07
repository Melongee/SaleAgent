from langchain.chains import LLMChain
from langchain_community.llms import BaseLLM
from utils.prompts import get_sales_conversation_prompt


class SalesConversationChain(LLMChain):
    """链式生成对话的下一个话语。"""

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        prompt = get_sales_conversation_prompt()
        return cls(prompt=prompt, llm=llm, verbose=verbose) 