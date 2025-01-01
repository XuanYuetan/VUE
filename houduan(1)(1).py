from flask import Flask, request, send_file
import cv2
import numpy as np
import tempfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 启用跨域支持


# 掐丝处理函数
def close_line_art(image):
    # 将上传的文件转换为 OpenCV 可处理的格式
    image_array = np.frombuffer(image.read(), np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)

    # 图像处理逻辑：掐丝（闭合线条）
    _, binary = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY_INV)
    kernel_close = np.ones((4, 4), np.uint8)
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_close)
    kernel_connect = np.ones((2, 2), np.uint8)
    connected = cv2.dilate(closed, kernel_connect, iterations=1)
    connected = cv2.erode(connected, kernel_connect, iterations=1)

    # 替换颜色为蓝绿红（掐丝颜色）
    colored_image = np.ones((connected.shape[0], connected.shape[1], 3), dtype=np.uint8) * 255  # 初始化为白色背景
    colored_image[connected == 255] = [100, 170, 200]  # 蓝绿红色

    return colored_image

# 路由处理
@app.route('/', methods=['POST'])
def handle_close_line_art():
    if 'image' not in request.files:
        return "No image file provided", 400

    # 获取上传的文件
    image_file = request.files['image']

    # 使用临时文件保存处理结果
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_output:
        processed_image = close_line_art(image_file)
        cv2.imwrite(temp_output.name, processed_image)
        return send_file(temp_output.name, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
