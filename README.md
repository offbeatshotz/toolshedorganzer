# 🛠️ Workbench Layout Grid (Vercel Edition)

A high-performance, single-screen workspace planner that allows you to simulate multiple workbench layouts simultaneously using a grid-tile system.

## 🌟 New Features
- **No-Scroll Interface**: Optimized to fit perfectly on any screen (mobile or desktop) without scrolling.
- **Multi-Tile Grid**: Simulate up to 6 different workbench layouts side-by-side.
- **Drag & Drop Support**: Drop your own workbench images directly into any tile to start simulating.
- **Per-Tile Camera Capture**: Click any empty tile to snap a photo and instantly start repositioning.
- **Independent Simulations**: Each tile operates independently with its own selection and move logic.

## 🚀 How to Use
1. **Load Images**: Drag an image file into a tile OR click a tile to use your camera.
2. **Select**: Click the **SELECT** button on a tile and drag a box over your workbench.
3. **Lock**: Click **LOCK** once you've selected the area.
4. **Move**: Drag the cutout workbench anywhere within that tile to see how it looks!
5. **Reset**: Use the **X** on a tile to clear it, or the **Reset Grid** button to start over completely.

## 🌐 Deployment to Vercel
1. Push your code to a GitHub repository.
2. Import the repository into [Vercel](https://vercel.com/).
3. Enjoy your live, high-speed workspace planner!

## 🛠️ Local Development
1. `pip install -r requirements.txt`
2. `python api/index.py`
3. Visit `http://localhost:5000`
