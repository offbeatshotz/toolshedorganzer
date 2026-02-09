import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# Set page layout
st.set_page_config(page_title="Workbench Re-positioner", layout="wide")

st.title("🛠️ Workbench Move & Reposition Simulator")
st.markdown("""
Capture your workspace, select your workbench, and virtually move it to see how a new layout would look!
""")

# Session state initialization
if 'image_captured' not in st.session_state:
    st.session_state.image_captured = None
if 'workbench_cutout' not in st.session_state:
    st.session_state.workbench_cutout = None
if 'selection_coords' not in st.session_state:
    st.session_state.selection_coords = (100, 100, 300, 200) # x, y, w, h

# Camera Input
camera_image = st.camera_input("Take a photo of your current workbench area")

if camera_image:
    # Convert camera image to numpy array
    img = Image.open(camera_image)
    img_np = np.array(img)
    st.session_state.image_captured = img_np

if st.session_state.image_captured is not None:
    img_np = st.session_state.image_captured
    h, w, _ = img_np.shape

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Select Workbench Area")
        st.write("Adjust the sliders to box your workbench.")
        
        # Selection Sliders
        sel_x = st.slider("Selection X", 0, w, st.session_state.selection_coords[0])
        sel_y = st.slider("Selection Y", 0, h, st.session_state.selection_coords[1])
        sel_w = st.slider("Selection Width", 10, w - sel_x, st.session_state.selection_coords[2])
        sel_h = st.slider("Selection Height", 10, h - sel_y, st.session_state.selection_coords[3])
        
        st.session_state.selection_coords = (sel_x, sel_y, sel_w, sel_h)

        # Draw selection preview
        preview_img = img_np.copy()
        cv2.rectangle(preview_img, (sel_x, sel_y), (sel_x + sel_w, sel_y + sel_h), (255, 0, 0), 5)
        st.image(preview_img, caption="Current Selection", use_container_width=True)

        if st.button("✂️ Cut Out Workbench"):
            st.session_state.workbench_cutout = img_np[sel_y:sel_y+sel_h, sel_x:sel_x+sel_w].copy()
            st.success("Workbench captured! Now move it in the next section.")

    with col2:
        st.subheader("2. Reposition & Simulate")
        if st.session_state.workbench_cutout is not None:
            # Movement Sliders
            move_x = st.slider("New X Position", 0, w - sel_w, sel_x)
            move_y = st.slider("New Y Position", 0, h - sel_h, sel_y)
            
            # Create simulation
            # Option to hide original workbench (fill with mean color or blurred background)
            hide_original = st.checkbox("Hide original workbench area?", value=True)
            
            sim_img = img_np.copy()
            
            if hide_original:
                # Fill original area with a simple blur or gray to 'remove' it
                original_x, original_y, original_w, original_h = st.session_state.selection_coords
                sim_img[original_y:original_y+original_h, original_x:original_x+original_w] = cv2.blur(
                    sim_img[original_y:original_y+original_h, original_x:original_x+original_w], (50, 50)
                )

            # Paste cutout at new location
            cutout = st.session_state.workbench_cutout
            sim_img[move_y:move_y+sel_h, move_x:move_x+sel_w] = cutout
            
            # Draw a border around the moved workbench
            cv2.rectangle(sim_img, (move_x, move_y), (move_x + sel_w, move_y + sel_h), (0, 255, 0), 3)
            
            st.image(sim_img, caption="New Layout Simulation", use_container_width=True)
            
            # Download result
            result_pil = Image.fromarray(sim_img)
            buf = io.BytesIO()
            result_pil.save(buf, format="PNG")
            st.download_button("💾 Download New Layout", buf.getvalue(), "new_layout.png", "image/png")
        else:
            st.info("Cut out a workbench from the left side to start simulating.")

    if st.button("🔄 Reset Everything"):
        st.session_state.image_captured = None
        st.session_state.workbench_cutout = None
        st.rerun()

else:
    st.info("Waiting for camera capture... Please take a photo to begin.")
    st.image("https://images.unsplash.com/photo-1581244277943-fe4a9c777189?auto=format&fit=crop&q=80&w=1000", 
             caption="Example Workspace", use_container_width=True)

st.sidebar.markdown("""
### How to use:
1. **Snap:** Take a photo of your room.
2. **Select:** Use sliders to box your workbench.
3. **Cut:** Click 'Cut Out Workbench'.
4. **Move:** Use sliders to reposition it.
5. **Save:** Download your new design!
""")
