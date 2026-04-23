# Product Customization Studio ✨

A high-performance, full-stack product customization system. This platform allows users to upload custom artwork (logos, drawings, designs) and automatically renders highly realistic, 3D-mapped mockups across a variety of photorealistic product bases (Hoodies, T-Shirts, Caps, and Mugs).

## Features

- **Pro Interactive Editor:** A fully integrated UI allowing users to independently scale (X/Y), rotate, and offset their designs *before* rendering.
- **Advanced 3D Mapping:** 
  - **Cylindrical Warping:** Custom OpenCV algorithms curve artwork naturally around cylindrical surfaces like coffee mugs.
  - **Deep Fabric Displacement:** Advanced contrast-boosted displacement mapping naturally wraps designs into the shadows, folds, and wrinkles of fabric.
- **High-Resolution Photorealistic Assets:** Uses 4K studio-lit base images mapped with exact mathematical coordinates for flawless results.
- **Automatic Multi-Product Generation:** One upload automatically generates mockups across all available products and views simultaneously.
- **Asynchronous Processing:** Built to scale using Celery and Redis to handle heavy computer vision operations off the main API thread.

---

## Tech Stack

### Frontend
- **React.js (Vite)**
- **CSS3** (Custom Premium Styling with Light/Dark Mode)
- **Lucide React** (Iconography)

### Backend
- **Python / Django REST Framework**
- **OpenCV & NumPy** (Core image processing engine)
- **Celery** (Task Queue)
- **Redis** (Message Broker) - *(Currently set to eager execution for local testing)*
- **SQLite** (Database)

---

## Getting Started

Follow these instructions to get the project running on your local machine.

### 1. Backend Setup (Django)

1. **Navigate to the project root directory:**
   ```bash
   cd Product-Customization-System
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Seed the database with high-resolution assets:**
   *(This script automatically cleans the DB, uploads the HQ base images, and defines the perfect print area coordinates).*
   ```bash
   python seed_hq_products.py
   python add_hoodie_back.py
   ```

5. **Start the Django server:**
   ```bash
   python manage.py runserver
   ```
   *The API will be available at `http://127.0.0.1:8000/`*

### 2. Frontend Setup (React/Vite)

1. **Open a new terminal and navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install node dependencies:**
   ```bash
   npm install
   ```

3. **Start the Vite development server:**
   ```bash
   npm run dev
   ```
   *The UI will be available at `http://localhost:5174/`*

---

## Project Structure

```
Product-Customization-System/
├── frontend/                  # React + Vite UI Application
│   ├── src/
│   │   ├── App.jsx            # Main App Component & Pro Editor logic
│   │   ├── index.css          # Styling & Theming
│   │   └── utils/             # Helper functions
├── customization_engine/      # Django Project Settings
├── products/                  # Django App (Models, Serializers, API Views)
├── processor/                 # Django App (OpenCV Engine & Celery Tasks)
│   ├── engine.py              # Core OpenCV logic (Warping, Displacement, Blending)
│   └── tasks.py               # Asynchronous Celery workers
├── media/                     # Stored base images and generated mockups
├── seed_hq_products.py        # Automation script to populate database
└── requirements.txt           # Python dependencies
```

## Deployment Recommendations

- **Frontend:** [Netlify](https://www.netlify.com/) or Vercel. Set build command to `npm run build` and publish directory to `dist`.
- **Backend:** [Render](https://render.com/) or [Railway](https://railway.app/). These services support Python environments, OpenCV libraries, and background worker processes required for the image generation engine.
