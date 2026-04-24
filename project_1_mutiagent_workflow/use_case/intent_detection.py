from domain.interfaces import IntentClassifier
from domain.ingredient import User_input, IntentAnalysis, IntentType


class IntentDetectionUseCase:
    def __init__(self, intent_classifier: IntentClassifier):
        self.intent_classifier = intent_classifier

    def execute(self, user_input: User_input) -> IntentAnalysis:
        if user_input.content == "":  # edge case
            return IntentAnalysis(
                primary_intent=IntentType.UNKNOWN,
                confidence=0.0,
                extracted_entities={},
                raw_reasoning="",
            )
        return self.intent_classifier.classify(user_input)
