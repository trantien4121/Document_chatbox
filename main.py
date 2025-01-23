from GeminiAI import GeminiAI
from ResumeParser import ResumeParser
from flask import Flask, request, render_template
import os

app = Flask(__name__, static_url_path='/static')
uploads_dir = os.path.join("resources", "input")

# Create new uploads forder if not exists
os.makedirs(uploads_dir, exist_ok=True)

# Create global variable
parsed_content = ""
uploaded_file_name = ""
chat_history = []  

def reset_globals(): 
    global parsed_content, uploaded_file_name, chat_history 
    parsed_content = "" 
    uploaded_file_name = "" 
    chat_history = []

def delete_all_files_in_directory(directory):
    # check if exists
    if os.path.exists(directory) and os.path.isdir(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Đã xóa: {file_path}")
    else:
        print(f"Thư mục không tồn tại: {directory}")

def delete_file_in_directory(directory, filename):
    # check folder if exist
    if os.path.exists(directory) and os.path.isdir(directory):
        file_path = os.path.join(directory, filename)
        #check file if exists
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Đã xóa: {file_path}")
        else:
            print(f"File không tồn tại: {file_path}")
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

            # Init GeminiAI và ResumeParser
            gemini = GeminiAI.get_instance()
            parser = ResumeParser(gemini)

            # Parse content from PDF file
            content = parser.extract_text_from_pdf(file_path)
            parsed_content.append(content)
            
            # Save fileName
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

@app.route('/delete_file', methods=['DELETE'])
def delete_file():
    filename = request.args.get('filename')
    delete_file_in_directory(uploads_dir, filename)
    return '', 204  # 204 No Content

def format_answer(text):
    print('Answer before format: ', text)
    text = text.strip()  # Remove space 
    text = text.replace('* **', '<br/>')  
    text = text.replace('**', '  ')  
    print('Answer before format br: ', text)
    lines = text.split('<br/>')  
    formatted_lines = ['<li>' + line.strip() + '</li>' for line in lines if line.strip()]  
    first_line = lines[0].strip() if lines else ""
    formatted_lines = ['<li>' + line.strip() + '</li>' for line in lines[1:] if line.strip()]  
    if formatted_lines:
        return first_line + '<ul>' + ''.join(formatted_lines) + '</ul>'
    else:
        return first_line 

if __name__ == "__main__":
    app.run(debug=True, port=8050, host='0.0.0.0')