import google.generativeai as genai
import os
from dotenv import load_dotenv

# load environment variable from file .env
load_dotenv()


# get api key from https://console.cloud.google.com/apis/credentials or https://aistudio.google.com/app/apikey
# define the model name and api key from environment variables
class GeminiAI:
    instance = None

    def __init__(self, api_key, model_name):
        genai.configure(api_key=api_key)
        self.instance = None
        self.model = genai.GenerativeModel(model_name)
        self.prompt = """
                {content}
            Dựa vào nội dung bên trên, không cần tóm tắt nội dung tài liệu, trả lời chính xác cho câu hỏi:
                {question}
        """

    @staticmethod
    def get_instance():
        if not GeminiAI.instance:
            model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
            api_key = os.getenv("API_KEY", "")
            GeminiAI.instance = GeminiAI(api_key=api_key, model_name=model_name)
        return GeminiAI.instance

    def explain_resume(self, content, question):
        model_content = self.prompt.replace("{content}", content)
        model_content = model_content.replace("{question}", question)
        print(question)
        response = self.model.generate_content(model_content)
        return response.text
    
    def summarize(self, content):
        # Create a prompt for summarization
        summarize_prompt = "Tóm tắt đoạn văn bản sau đây, lấy chuẩn sát nội dung và không thay thế bằng bất kỳ nội dung tổng quát nào khác, tập trung vào các ý chính và bỏ qua chi tiết không quan trọng, vừa lấy nội dung riêng, vừa lấy nội dung chung: {content}"
        model_content = summarize_prompt.replace("{content}", content)
        response = self.model.generate_content(model_content)
        return response.text
