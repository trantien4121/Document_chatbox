
from datetime import datetime

from GeminiAI import GeminiAI
from ResumeParser import ResumeParser
from flask import Flask, request, render_template, send_from_directory
import os
import re

# def main():
#     # Initialize the GeminiAI and ResumeParser classes
#     gemini = GeminiAI.get_instance()
#     parser = ResumeParser(gemini)

#     # # test time to parse a resume
#     # start = datetime.now()

#     file_path = "resources/input/Li_thuyet_Hadoop.pdf"
#     content = parser.extract_text_from_pdf(file_path)
#     # print(explanation)

#     # print("Time taken:", datetime.now() - start)
#     # ## average time taken: 0:00:02.5 seconds
#     awn = gemini.explain_resume(content, "Apache Zookeeper là gì?")
#     print(awn)

# if __name__ == "__main__":
#     main()

app = Flask(__name__, static_url_path='/static')
uploads_dir = os.path.join("resources", "input")

# Tạo thư mục uploads nếu chưa tồn tại
os.makedirs(uploads_dir, exist_ok=True)

# Biến toàn cục để lưu trữ nội dung đã phân tích và các câu hỏi, câu trả lời
parsed_content = ""
uploaded_file_name = ""
chat_history = []  # Danh sách lưu trữ câu hỏi và câu trả lời

@app.route('/')
def upload_form():
    return render_template('upload.html', answer=None, file_name=None, chat_history=chat_history)

@app.route('/upload', methods=['POST'])
def upload_file():
    global parsed_content, uploaded_file_name

    if 'file' not in request.files:
        return "Không có file nào được chọn", 400

    file = request.files['file']
    if file.filename == '':
        return "Không có file nào được chọn", 400

    if file and file.filename.endswith('.pdf'):
        file_path = os.path.join(uploads_dir, file.filename)
        file.save(file_path)

        # Khởi tạo GeminiAI và ResumeParser
        gemini = GeminiAI.get_instance()
        parser = ResumeParser(gemini)

        # Phân tích nội dung file PDF
        parsed_content = parser.extract_text_from_pdf(file_path)
        
        # Lưu tên file đã tải lên
        uploaded_file_name = file.filename
        
        return render_template('upload.html', answer=None, file_name=uploaded_file_name, chat_history=chat_history)

    return "Định dạng file không hợp lệ", 400

@app.route('/ask', methods=['POST'])
def ask_question():
    global parsed_content, chat_history, uploaded_file_name

    question = request.form['question']
    if parsed_content:
        gemini = GeminiAI.get_instance()
        answer = format_answer(gemini.explain_resume(parsed_content, question))
        print(answer);

        # Lưu câu hỏi và câu trả lời vào lịch sử chat
        chat_history.append({'question': question, 'answer': answer})

        return render_template('upload.html', answer=None, file_name=uploaded_file_name, chat_history=chat_history)

    return "Chưa có nội dung nào được phân tích.", 400

def format_answer(text):
    print('Answer before format: ', text)
    # Định dạng câu trả lời
    text = text.strip()  # Xóa khoảng trắng thừa
    # Thay thế * bằng xuống dòng
    text = text.replace('* **', '<br/>')  
    # Thay thế ** bằng dấu cách đôi
    text = text.replace('**', '  ')  
    print('Answer before format br: ', text)
    lines = text.split('<br/>')  # Chia văn bản thành các dòng dựa trên <br/>
    formatted_lines = ['<li>' + line.strip() + '</li>' for line in lines if line.strip()]  # Bọc mỗi dòng trong <li>
    # Nối lại các dòng và thêm <ul>
    # Lấy đoạn đầu tiên
    first_line = lines[0].strip() if lines else ""
    # Bọc các đoạn còn lại trong <li> và thêm <ul> ở đầu và </ul> ở cuối
    formatted_lines = ['<li>' + line.strip() + '</li>' for line in lines[1:] if line.strip()]  # Bọc mỗi dòng sau trong <li>
    
    # Nối lại các dòng và thêm <ul> nếu có
    if formatted_lines:
        return first_line + '<ul>' + ''.join(formatted_lines) + '</ul>'
    else:
        return first_line  # Chỉ trả về đoạn đầu nếu không có dòng nào khác

if __name__ == "__main__":
    app.run(debug=True, port=8050, host='0.0.0.0')