import google.generativeai as genai
import os
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()


# get api key from https://console.cloud.google.com/apis/credentials or https://aistudio.google.com/app/apikey
# define the model name and api key from environment variables
class GeminiAI:
    instance = None

    def __init__(self, api_key, model_name):
        genai.configure(api_key=api_key)
        self.instance = None
        self.model = genai.GenerativeModel(model_name)
    #     self.prompt =  """<|im_start|>system\nBản là một trợ lí AI hữu ích về pháp luật. Hãy trả lời câu hỏi chính xác, nếu bạn không biết câu trả lời, hãy nói không biết, đừng cố tạo ra câu trả lời\n

    # {context}<|im_end|>\n<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant"""
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
