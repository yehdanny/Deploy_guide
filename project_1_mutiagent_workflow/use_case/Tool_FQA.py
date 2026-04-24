from domain.interfaces import Tool_FQA
from domain.ingredient import User_input, ToolResult


class Tool_FQA_UseCase:
    def __init__(self, tool_fqa: Tool_FQA):
        self.tool_fqa = tool_fqa

    def execute(self, user_input: User_input) -> IntentAnalysis:
        if user_input.content == "":  # edge case
            return ToolResult(
                success=False,
                error_message="User input is empty",
                source_system="Tool_FQA",
            )
        reslut = self.tool_fqa.get_message(user_input)
        if reslut.similarity > 0.6:
            return reslut
        else:
            return ToolResult(
                success=False,
                error_message="User input is not match",
                source_system="Tool_FQA",
            )
