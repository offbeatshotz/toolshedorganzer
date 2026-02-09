from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
import io
from PIL import Image

app = Flask(__name__, template_folder='../templates')

def detect_workbenches(image):
    # Convert to grayscale and detect edges
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 30, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected = []
    output = image.copy()
    
    # Step 1: Find potential tops (horizontal rectangles)
    potential_tops = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 3000: continue
        
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w)/h
        
        # Table tops are usually wider than they are tall
        if aspect_ratio > 1.5:
            potential_tops.append({'x': x, 'y': y, 'w': w, 'h': h, 'cnt': cnt})

    # Step 2: For each top, look for legs beneath it
    for top in potential_tops:
        # Define search area for legs (directly below the top)
        leg_search_y = top['y'] + top['h']
        leg_search_h = int(top['h'] * 3) # Look down 3x the top's height
        
        # Look for vertical contours in the search area
        legs_found = 0
        for cnt in contours:
            lx, ly, lw, lh = cv2.boundingRect(cnt)
            
            # Is this contour below the current top and within its horizontal span?
            if (ly >= leg_search_y and ly <= leg_search_y + leg_search_h and 
                lx >= top['x'] - 20 and lx + lw <= top['x'] + top['w'] + 20):
                
                # Legs are usually taller than they are wide
                leg_aspect = float(lh)/lw if lw > 0 else 0
                if leg_aspect > 1.2 and cv2.contourArea(cnt) > 500:
                    legs_found += 1
                    # Draw legs in a different color for debugging/visuals
                    cv2.rectangle(output, (lx, ly), (lx + lw, ly + lh), (255, 165, 0), 2)

        # Step 3: If it has a top and at least one leg-like structure, it's a workbench/table
        if legs_found >= 1:
            x, y, w, h = top['x'], top['y'], top['w'], top['h']
            # Expand bounding box to include legs
            total_h = leg_search_h + h
            detected.append({'x': x, 'y': y, 'w': w, 'h': total_h, 'type': 'Workbench/Table'})
            
            # Draw main detection
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(output, f"Workbench (Legs: {legs_found})", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
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
