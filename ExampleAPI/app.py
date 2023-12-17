from flask import Flask, render_template, request
from convert import convert
import base64

app = Flask(__name__)

@app.route('/')
def home():
    return 'This is Example API!'

@app.route('/index')
def index():
    # 원하는 동적인 값 설정
    statement = convert()
    return render_template('template.html', string=statement)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        # 이미지 데이터를 받아서 저장
        image_data = request.form['image_data']
        save_image(image_data)
        return 'Image uploaded successfully.', 200
    except Exception as e:
        print(f'Error uploading image: {str(e)}')
        return 'Failed to upload image.', 500

def save_image(image_data):
    # 이미지 데이터를 디코딩하고 파일로 저장
    try:
        image_data_decoded = base64.b64decode(image_data.split(',')[1])
        with open('uploaded_image.png', 'wb') as f:
            f.write(image_data_decoded)
        print('Image saved successfully.')
    except Exception as e:
        print(f'Error saving image: {str(e)}')

if __name__ == '__main__':
    app.run(debug=True)
