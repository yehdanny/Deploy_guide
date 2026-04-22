from infrastructure.ollama_adapter import OllamaSummarizer
from use_cases.summarize_document import SummarizeDocumentUseCase

# 工人 (Infrastructure)
ai = OllamaSummarizer(model_name="qwen3:4b-instruct")

# 監工 (Use case)
app = SummarizeDocumentUseCase(ai_service=ai)

# 執行 (Use case . excute)
final_result = app.execute(
    "2008年，文章在熱播劇《奮鬥》中出演男二號向南，引起廣泛關注。這也是文章和妻子馬伊琍的第二次合作。2009年，文章進入電影屆，主演第一部電影《走著瞧》。該片在上海國際電影節新片展映單元和東京國際電影節「亞洲風」單元獲獎。文章也憑主演的北京青年馬傑一角獲得第12屆上海國際電影節最受關注新人演員獎。2009年，文章主演電視劇《愛在日月潭》，參演熱播電視劇《蝸居》，成功飾演配角小貝，知名度得到進一步提高。2010年，文章與李連杰共同主演文藝片《海洋天堂》，文章飾演自閉症青年大福，被認為是中國的「達斯汀·霍夫曼」。文章憑此片獲得第14屆中國電影華表獎優秀新人男演員獎，第13屆上海國際電影節最佳男主角獎和第18屆北京大學生電影節最受大學生歡迎男演員獎。該片獲得上海國際電影節「金爵獎」，中國電影華表獎優秀故事片獎和第18屆北京大學生電影節人文關懷獎。同年，文章主演電視劇《雪豹》，該劇被各大電視台反覆播放。文章憑藉周衛國一角獲得第12屆四川電視藝術節金熊貓獎電視劇類最佳男演員，第9屆中國金鷹電視藝術節最具人氣男演員和第26屆中國電視金鷹獎觀眾喜愛的男演員獎項。",
    source="wikipedia",
)

print(f"最終摘要結果：{final_result.raw_text}")
