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
    
    # Use adaptive thresholding to handle varied lighting in sheds
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                 cv2.THRESH_BINARY_INV, 11, 2)
    
    # Morphological operations to close gaps in lines
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected = []
    output = image.copy()
    h_img, w_img = image.shape[:2]
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # Filter out noise (too small) or the whole frame (too big)
        if area < (w_img * h_img * 0.02) or area > (w_img * h_img * 0.8):
            continue
            
        # Get bounding box
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w)/h
        
        # Heuristic for Workbenches/Tables/Desks:
        # 1. Usually wider than they are tall (0.8 to 4.0 aspect ratio)
        # 2. Usually located in the lower 2/3 of the image
        if 0.7 < aspect_ratio < 5.0 and y > (h_img * 0.1):
            # Refine the contour to see if it's rectangular-ish
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
            
            # We are more permissive now: if it's a large enough boxy shape, we flag it
            detected.append({
                'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h), 
                'type': 'Workbench/Surface'
            })
            
            # Draw the detection
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(output, "Surface Detected", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

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
