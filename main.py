from GeminiAI import GeminiAI
from ResumeParser import ResumeParser
from flask import Flask, request, render_template
import os

app = Flask(__name__, static_url_path='/static')
uploads_dir = os.path.join("resources", "input")

# Tạo thư mục uploads nếu chưa tồn tại
os.makedirs(uploads_dir, exist_ok=True)

# Biến toàn cục để lưu trữ nội dung đã phân tích và các câu hỏi, câu trả lời
parsed_content = ""
uploaded_file_name = ""
chat_history = []  # Danh sách lưu trữ câu hỏi và câu trả lời

def reset_globals(): 
    global parsed_content, uploaded_file_name, chat_history 
    parsed_content = "" 
    uploaded_file_name = "" 
    chat_history = []

def delete_all_files_in_directory(directory):
    # check if exist
    if os.path.exists(directory) and os.path.isdir(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Đã xóa: {file_path}")
    else:
        print(f"Thư mục không tồn tại: {directory}")

@app.route('/')
def upload_form():
    delete_all_files_in_directory(uploads_dir)
    reset_globals()
    return render_template('upload.html', answers=None, file_names=None, chat_history=chat_history)

@app.route('/upload', methods=['POST'])
def upload_file():
    global parsed_content, uploaded_file_names

    if 'files' not in request.files:
        return "Không có file nào được chọn", 400

    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        return "Không có file nào được chọn", 400

    uploaded_file_names = []
    parsed_content = []

    for file in files:
        if file and file.filename.endswith('.pdf'):
            file_path = os.path.join(uploads_dir, file.filename)
            file.save(file_path)

            # Khởi tạo GeminiAI và ResumeParser
            gemini = GeminiAI.get_instance()
            parser = ResumeParser(gemini)

            # Phân tích nội dung file PDF
            content = parser.extract_text_from_pdf(file_path)
            parsed_content.append(content)
            
            # Lưu tên file đã tải lên
            uploaded_file_names.append(file.filename)
            print(file.filename)
            print("===> Parsed_content size: ", len(parsed_content))

    if not uploaded_file_names:
        return "Định dạng file không hợp lệ", 400

    return render_template('upload.html', answers=None, file_names=uploaded_file_names, chat_history=chat_history)


@app.route('/ask', methods=['POST'])
def ask_question():
    global parsed_content, chat_history, uploaded_file_names

    question = request.form['question']
    if parsed_content:
        gemini = GeminiAI.get_instance()
        answers = []

        for content in parsed_content:
            answer = format_answer(gemini.explain_resume(content, question))
            print(answer);
            answers.append(answer)

        # Lưu câu hỏi và câu trả lời vào lịch sử chat
        chat_history.append({'question': question, 'answers': answers})

        return render_template('upload.html', answers=answers, file_names=uploaded_file_names, chat_history=chat_history)

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