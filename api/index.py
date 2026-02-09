from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
import io
from PIL import Image

app = Flask(__name__, template_folder='../templates')

def detect_workbenches(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Edge detection
    edged = cv2.Canny(blurred, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected = []
    output = image.copy()
    
    for cnt in contours:
        # Approximate the contour to a polygon
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        
        # Workbenches are usually large rectangular surfaces
        # We look for 4-sided polygons with a significant area
        area = cv2.contourArea(cnt)
        if len(approx) == 4 and area > 5000:
            x, y, w, h = cv2.boundingRect(approx)
            detected.append({'x': x, 'y': y, 'w': w, 'h': h})
            # Draw on output
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(output, "Workbench?", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
    return output, detected

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image():
    data = request.json
    if 'image' not in data:
        return jsonify({'error': 'No image provided'}), 400
    
    # Decode base64 image
    img_data = base64.b64decode(data['image'].split(',')[1])
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Detect workbenches
    processed_img, detections = detect_workbenches(img)
    
    # Encode back to base64
    _, buffer = cv2.imencode('.jpg', processed_img)
    processed_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return jsonify({
        'image': f"data:image/jpeg;base64,{processed_base64}",
        'detections': detections
    })

if __name__ == '__main__':
    app.run(debug=True)
