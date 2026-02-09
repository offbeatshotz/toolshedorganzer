import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# Set page config
st.set_page_config(page_title="Toolshed Organizer AI", layout="wide")

st.title("🛠️ Toolshed Organizer & Simulator")
st.markdown("""
Reorganize your space virtually! Capture your current toolshed layout and simulate new organization ideas with unlimited possibilities.
""")

# Initialize session state for simulations
if 'simulations' not in st.session_state:
    st.session_state.simulations = []

# Sidebar for controls
st.sidebar.header("Settings & Tools")
tool_shape = st.sidebar.radio("Item Shape", ["Rectangle", "Circle"])
tool_type = st.sidebar.selectbox("Select Item to Simulate", 
    ["Shelf", "Tool Rack", "Workbench", "Storage Bin", "Wall Hook", "Cabinet", "Trash Can", "Drill Station"])

tool_color = st.sidebar.color_picker("Item Color", "#00FFAA")
tool_opacity = st.sidebar.slider("Opacity", 0.1, 1.0, 0.6)

# Main Camera Input
img_file = st.camera_input("Take a photo of your toolshed")

if img_file:
    # Convert the file to an OpenCV image
    bytes_data = img_file.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    
    h, w, _ = cv2_img.shape

    st.subheader("Simulate Your New Layout")
    
    col1, col2 = st.columns([3, 1.5])

    with col2:
        st.write("### Add New Item")
        pos_x = st.slider("X Position", 0, w, w // 2)
        pos_y = st.slider("Y Position", 0, h, h // 2)
        
        if tool_shape == "Rectangle":
            item_w = st.slider("Width", 10, w // 2, 100)
            item_h = st.slider("Height", 10, h // 2, 100)
            radius = 0
        else:
            radius = st.slider("Radius", 5, w // 4, 50)
            item_w, item_h = 0, 0
        
        if st.button("Add to Simulation"):
            st.session_state.simulations.append({
                "type": tool_type,
                "shape": tool_shape,
                "x": pos_x,
                "y": pos_y,
                "w": item_w,
                "h": item_h,
                "radius": radius,
                "color": tool_color,
                "opacity": tool_opacity
            })
            st.success(f"Added {tool_type}!")

        if st.button("Clear All Simulations"):
            st.session_state.simulations = []
            st.rerun()
        
        st.write("---")
        st.write("### Current Items")
        for i, item in enumerate(st.session_state.simulations):
            col_a, col_b = st.columns([3, 1])
            col_a.write(f"{i+1}. {item['type']}")
            if col_b.button("🗑️", key=f"del_{i}"):
                st.session_state.simulations.pop(i)
                st.rerun()

    with col1:
        # Create a copy of the image to draw on
        canvas = cv2_img.copy()
        overlay = canvas.copy()

        # Draw all simulations
        for item in st.session_state.simulations:
            # Hex to RGB
            hex_color = item['color'].lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            x, y = item['x'], item['y']
            
            if item['shape'] == "Rectangle":
                iw, ih = item['w'], item['h']
                cv2.rectangle(overlay, (x, y), (x + iw, y + ih), rgb, -1)
                cv2.putText(overlay, item['type'], (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            else:
                r = item['radius']
                cv2.circle(overlay, (x, y), r, rgb, -1)
                cv2.putText(overlay, item['type'], (x - r, y - r - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Blend the overlay with the original image
        cv2.addWeighted(overlay, tool_opacity, canvas, 1 - tool_opacity, 0, canvas)
        
        st.image(canvas, caption="Virtual Simulation Preview", use_container_width=True)

    # Export functionality
    if st.session_state.simulations:
        st.write("---")
        st.write("### Current Plan Summary")
        for i, item in enumerate(st.session_state.simulations):
            st.write(f"{i+1}. **{item['type']}** at ({item['x']}, {item['y']}) size {item['w']}x{item['h']}")
        
        # Option to download the simulation
        result_img = Image.fromarray(canvas)
        buf = io.BytesIO()
        result_img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button(label="Download Simulation Image", data=byte_im, file_name="toolshed_plan.png", mime="image/png")

else:
    st.info("Please allow camera access and take a photo to start organizing!")
    
    # Placeholder for what it looks like
    st.image("https://images.unsplash.com/photo-1581244277943-fe4a9c777189?auto=format&fit=crop&q=80&w=1000", 
             caption="Example Toolshed (Take your own photo to start!)", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("""
**How to use:**
1. Snap a photo of your messy toolshed.
2. Select a tool/storage item from the sidebar.
3. Use the sliders to place it in the image.
4. Click 'Add to Simulation' to lock it in.
5. Create as many simulations as you want!
""")
