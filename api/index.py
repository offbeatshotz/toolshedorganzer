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
    
    # IMPROVEMENT 1: Use CLAHE (Contrast Limited Adaptive Histogram Equalization)
    # This significantly helps in low-light toolsheds or garage environments
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)
    
    # IMPROVEMENT 2: Dual-path detection (Hough Lines + Contours)
    # Path A: Hough Lines for structured workstations (Tops + Legs)
    edged = cv2.Canny(enhanced_gray, 50, 150)
    lines = cv2.HoughLinesP(edged, 1, np.pi/180, threshold=40, minLineLength=60, maxLineGap=20)
    
    detected = []
    output = image.copy()
    processed_tops = []

    # Helper to avoid overlapping boxes
    def is_redundant(new_box):
        for box in detected:
            # If 70% of the new box is inside an existing box, it's redundant
            ix = max(new_box['x'], box['x'])
            iy = max(new_box['y'], box['y'])
            iw = min(new_box['x'] + new_box['w'], box['x'] + box['w']) - ix
            ih = min(new_box['y'] + new_box['h'], box['y'] + box['h']) - iy
            if iw > 0 and ih > 0:
                overlap = (iw * ih) / (new_box['w'] * new_box['h'])
                if overlap > 0.7: return True
        return False

    if lines is not None:
        horizontal_lines = []
        vertical_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            dx, dy = abs(x2-x1), abs(y2-y1)
            if dx > dy * 3: horizontal_lines.append(line[0])
            elif dy > dx * 2: vertical_lines.append(line[0])

        for h_line in horizontal_lines:
            hx1, hy1, hx2, hy2 = sorted([h_line[0], h_line[2]]), h_line[1], sorted([h_line[0], h_line[2]]), h_line[3]
            hx1, hx2 = hx1[0], hx1[1] # Endpoints sorted L to R
            
            legs = 0
            max_ly = hy1
            for v_line in vertical_lines:
                vx, vy1, _, vy2 = v_line
                vy_min, vy_max = min(vy1, vy2), max(vy1, vy2)
                if abs(vy_min - hy1) < 40 and hx1-20 <= vx <= hx2+20:
                    legs += 1
                    max_ly = max(max_ly, vy_max)
                    cv2.line(output, (vx, vy_min), (vx, vy_max), (255, 100, 0), 3)

            if legs >= 1:
                new_box = {'x': int(hx1), 'y': int(hy1), 'w': int(hx2-hx1), 'h': int(max_ly-hy1), 'type': 'Workstation (AI Line)'}
                if not is_redundant(new_box):
                    detected.append(new_box)
                    cv2.rectangle(output, (hx1, hy1), (hx2, max_ly), (0, 255, 0), 2)

    # Path B: Contour detection for solid/cluttered workstations
    # Sometimes lines are broken by tools; contours can find the whole mass
    _, thresh = cv2.threshold(enhanced_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    h_img, w_img = image.shape[:2]
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < (w_img * h_img * 0.05): continue # Must be a significant surface
        
        x, y, w, h = cv2.boundingRect(cnt)
        if w > h * 1.2 and y > h_img * 0.2: # Typical workbench proportions and position
            new_box = {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h), 'type': 'Surface (AI Mass)'}
            if not is_redundant(new_box):
                detected.append(new_box)
                cv2.rectangle(output, (x, y), (x+w, y+h), (0, 200, 255), 2)

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
