# 🛠️ Toolshed Organizer AI

A Python-based web application that helps you reorganize your toolshed virtually. Capture a photo of your space and simulate new layouts with unlimited virtual tools and storage units.

## 🌟 Features

- **Live Camera Input:** Snap a photo of your current space directly from the app.
- **Virtual Overlays:** Add shelves, tool racks, workbenches, and more.
- **Customizable Shapes:** Choose between rectangles and circles for different storage types.
- **Simulation Control:** Adjust position, size, color, and opacity of virtual items.
- **Export Plans:** Download your simulated layout as a PNG image to guide your physical reorganization.

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd toolshed-organizer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## 🌐 How to Host on Vercel (Recommended)

This app is now optimized for Vercel deployment using Python Serverless Functions.

1. **Push to GitHub**: Upload all files to your repository.
2. **Deploy to Vercel**:
   - Go to [Vercel](https://vercel.com/).
   - Import your repository.
   - Vercel will automatically detect the Python environment and the `api/` directory.
   - Click **Deploy**.

## 🧠 AI Features: Workbench Detection

The app now automatically detects potential workbenches from your camera feed:
- **Computer Vision:** Uses OpenCV contour analysis to identify large, rectangular surfaces typically found in a toolshed.
- **Smart Highlighting:** Detected areas are outlined in green and labeled automatically.
- **Interactive:** Snap a photo to see what the AI finds and start organizing around it.

## 🚀 How to Run Locally (Vercel Version)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask app:**
   ```bash
   python api/index.py
   ```
   Open `http://localhost:5000` in your browser.

---
## 🛠️ Built With

- [Flask](https://flask.palletsprojects.com/) - Lightweight web framework.
- [Vercel](https://vercel.com/) - Serverless deployment platform.
- [OpenCV](https://opencv.org/) - Computer vision for workbench detection.
- [Tailwind CSS](https://tailwindcss.com/) - Modern styling for the UI.

---
*Created with ❤️ for better organization.*
