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
    
    # Use Canny with wider thresholds for better edge capture
    edged = cv2.Canny(gray, 50, 200)
    
    # Use Probabilistic Hough Line Transform to find line segments
    # This is much better for finding "legs" and "table tops"
    lines = cv2.HoughLinesP(edged, 1, np.pi/180, threshold=50, minLineLength=40, maxLineGap=10)
    
    detected = []
    output = image.copy()
    
    if lines is not None:
        horizontal_lines = []
        vertical_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            
            # Categorize lines by orientation
            if dx > dy * 3: # Horizontal
                horizontal_lines.append(line[0])
                # Draw horizontal lines in green (internal debug)
                # cv2.line(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
            elif dy > dx * 2: # Vertical
                vertical_lines.append(line[0])
                # Draw vertical lines in orange (internal debug)
                # cv2.line(output, (x1, y1), (x2, y2), (0, 165, 255), 2)

        # Step 2: Match legs to tops
        # For each horizontal line (potential top), see if there are vertical lines (legs) near its ends
        processed_tops = []
        for h_line in horizontal_lines:
            hx1, hy1, hx2, hy2 = h_line
            # Sort endpoints left-to-right
            if hx1 > hx2: hx1, hy1, hx2, hy2 = hx2, hy2, hx1, hy1
            
            legs_for_this_top = 0
            leg_y_max = hy1
            
            for v_line in vertical_lines:
                vx1, vy1, vx2, vy2 = v_line
                # Sort endpoints top-to-bottom
                if vy1 > vy2: vx1, vy1, vx2, vy2 = vx2, vy2, vx1, vy1
                
                # Check if vertical line starts near the horizontal line and is below it
                # Relaxed proximity: within 30 pixels horizontally of the top's span
                if (vy1 >= hy1 - 20 and vy1 <= hy1 + 50 and 
                    vx1 >= hx1 - 30 and vx1 <= hx2 + 30):
                    legs_for_this_top += 1
                    leg_y_max = max(leg_y_max, vy2)
                    # Highlight the detected leg
                    cv2.line(output, (vx1, vy1), (vx2, vy2), (0, 165, 255), 3)

            # If we found a horizontal surface with at least 1 leg (usually 2+ but 1 is safer for side views)
            if legs_for_this_top >= 1:
                # Group nearby horizontal lines to avoid duplicate detections
                is_duplicate = False
                for p_top in processed_tops:
                    if abs(p_top[1] - hy1) < 40: # Same vertical level
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    w = hx2 - hx1
                    h = leg_y_max - hy1
                    detected.append({
                        'x': int(hx1), 'y': int(hy1), 'w': int(w), 'h': int(h), 
                        'type': f'Workbench ({legs_for_this_top} legs)'
                    })
                    processed_tops.append((hx1, hy1, hx2, hy2))
                    
                    # Draw main detection
                    cv2.rectangle(output, (hx1, hy1), (hx2, leg_y_max), (0, 255, 0), 3)
                    cv2.putText(output, "WORKSTATION", (hx1, hy1 - 10), 
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
