from .ingredient import User_input, IntentAnalysis, ToolResult, CustomerResponse
from abc import ABC, abstractmethod


class IntentClassifier(ABC):
    @abstractmethod
    def classify(self, request: User_input) -> IntentAnalysis:
        pass


class Tool_FQA(ABC):
    @abstractmethod
    def get_message(self, request: User_input) -> ToolResult:
        pass


class Tool_DB(ABC):
    @abstractmethod
    def get_message(self, request: User_input) -> ToolResult:
        pass


class Tool_LLM(ABC):
    @abstractmethod
    def get_message(self, request: User_input) -> ToolResult:
        pass
