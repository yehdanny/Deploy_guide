import argparse
from infrastructure.ollama_adapter import OllamaSummarizer
from use_cases.summarize_document import SummarizeDocumentUseCase


def main(args):
    if args.model not in [
        "llama3:latest",
        "qwen3:4b-instruct",
        "qwen3:4b-instruct-2507-fp16",
        "codellama:latest",
        "deepseek-coder:latest",
        "gpt-3",  # cli不擋，但會被infrastructure擋
    ]:
        print("[app_cli] Invalid model name")
        return

    # 工人 (Infrastructure)
    ai = OllamaSummarizer(model_name=args.model)

    # 監工 (Use case)
    app = SummarizeDocumentUseCase(ai_service=ai)

    # 執行 (Use case . excute)
    text_input = input("\n\n請輸入要摘要的文字：")
    try:
        final_result = app.execute(text=text_input, source="CLI_User")
    except Exception as e:
        print(f"\n\n錯誤：{e}")
        return

    print(f"\n\n最終摘要結果：{final_result.raw_text}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple greeting script")
    parser.add_argument(
        "--model",
        type=str,
        default="llama3:latest",
        help="llama3:latest, qwen3:4b-instruct, qwen3:4b-instruct-2507-fp16, codellama:latest, deepseek-coder:latest",
    )
    args = parser.parse_args()

    main(args=args)
