# 🛠️ Workbench Re-positioner Simulator

A Python web application that uses your camera to virtually move and reposition workbenches in your workspace.

## 🚀 Features
- **Live Camera Capture:** Take a photo of your actual workspace.
- **Workbench Selection:** Use interactive sliders to select the exact area of your workbench.
- **Virtual Repositioning:** Move the selected workbench to any new location in the room.
- **Visual Simulation:** Automatically blurs the original location to show what the room looks like with the workbench moved.
- **Export Plan:** Download your new layout as a PNG image.

## 🛠️ Installation & Local Run
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd toolshed-organizer
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## 🌐 Deployment to GitHub & Streamlit Cloud
1. Push your code to a GitHub repository.
2. Go to [Streamlit Cloud](https://share.streamlit.io/).
3. Connect your GitHub account and select this repository.
4. Set the main file path to `app.py`.
5. Click **Deploy**!

## 📦 Dependencies
- `streamlit`
- `opencv-python-headless`
- `numpy`
- `Pillow`
