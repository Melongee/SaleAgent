from langchain.chains import LLMChain
from langchain_community.llms import BaseLLM
from utils.prompts import get_stage_analyzer_prompt


class StageAnalyzerChain(LLMChain):
    """链来分析对话应该进入哪个对话阶段。"""

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        """获取响应解析器。"""
        prompt = get_stage_analyzer_prompt()
        return cls(prompt=prompt, llm=llm, verbose=verbose) 