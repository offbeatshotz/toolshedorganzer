# 🛠️ Workbench Re-positioner Simulator (Vercel Edition)

A web application optimized for Vercel that allows you to virtually move and reposition workbenches in your workspace using your camera.

## 🚀 Features
- **Live Camera Capture:** Snap photos directly in the browser.
- **Interactive Cutout:** Drag a box to select exactly what you want to move.
- **Real-time Drag & Drop:** Move your workbench cutout around the room instantly.
- **Fast & Lightweight:** Built with Flask and Vanilla JS for zero lag.

## 🌐 Deployment to Vercel
1. Push your code to a GitHub repository.
2. Go to [Vercel](https://vercel.com/).
3. Import your GitHub repository.
4. Vercel will automatically detect the Flask project (via `api/index.py`).
5. Click **Deploy**!

## 🛠️ Local Development
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the development server:
   ```bash
   python api/index.py
   ```
3. Open `http://localhost:5000` in your browser.

## 📂 Project Structure
- `api/index.py`: Flask backend entry point for Vercel.
- `templates/index.html`: The core logic (Camera, Canvas, Drag & Drop).
- `vercel.json`: Deployment configuration.
