# VyaparAI - Intelligent E-commerce Platform

VyaparAI is a next-generation e-commerce solution that integrates **Natural Language Processing (NLP)** to revolutionize how users interact with data. It features a conversational "Talk-to-Your-Data" interface for admins and a smart shopping assistant for customers.

## 🚀 Features

### 🛍️ Client / Customer App
- **Product Browsing**: Clean, responsive, and high-performance catalog.
- **Smart Search**: Find products using natural language queries (e.g., "Show me healthy snacks under ₹200").
- **Cart & Checkout**: Full e-commerce flow with cart management.
- **Order History**: Track past orders and status.

### 🛡️ Admin Dashboard
- **Analytics Dashboard**: Real-time stats on Revenue, Users, Orders, and Low Stock.
- **AI Analytics Assistant**: Ask questions about your business in plain English (e.g., "What is my best selling category?", "Show me orders from last week").
- **Inventory Management**: Add, edit, and delete products easily with image uploads.
- **User Management**: View user details and sync with authentication provider.

## 🛠️ Tech Stack

### Frontend
- **Framework**: React (Vite)
- **Language**: TypeScript
- **Styling**: Tailwind CSS, Shadcn/UI
- **State Management**: TanStack Query (React Query)
- **Authentication**: Clerk
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (NeonDB)
- **ORM/Driver**: Psycopg (Raw SQL for performance & NL2SQL compatibility)
- **AI/LLM**: Google Gemini (via `google-generativeai`)
- **Image Storage**: Cloudinary

### Deployment
- **Backend**: Render (Web Service)
- **Frontend**: Netlify / Vercel (Recommended)

### Output Images
<img width="1463" height="814" alt="Screenshot 2025-12-07 at 11 02 54 PM" src="https://github.com/user-attachments/assets/5de537a6-c6fb-4d97-bf0c-8fef6d6e36c5" />

<img width="1465" height="850" alt="Screenshot 2025-12-07 at 11 16 55 PM" src="https://github.com/user-attachments/assets/e285ed29-3b11-4c46-975f-e513c943f1a9" />

<img width="1466" height="815" alt="Screenshot 2025-12-07 at 11 18 08 PM" src="https://github.com/user-attachments/assets/94602838-3653-4ca8-9adf-c3f26b524f21" />
<img width="1467" height="814" alt="Screenshot 2025-12-07 at 11 19 31 PM" src="https://github.com/user-attachments/assets/0b2d8a27-931d-45d9-b726-380313898333" />


## 📂 Project Structure

```
VyaparAI/
├── backend/                # FastAPI Backend
│   ├── core/               # AI & Pipeline Logic (NL2SQL)
│   ├── routers/            # API Endpoints
│   ├── main.py             # Entry Point
│   └── requirements.txt    # Python Dependencies
├── vyaparai-commerce-platform/  # React Frontend
│   ├── src/
│   │   ├── components/     # Reusable UI Components
│   │   ├── pages/          # App Pages (Dashboard, Store, Cart)
│   │   └── lib/            # Utilities (API, Utils)
│   └── package.json
└── render.yaml             # Render Deployment Config
```

## 🔧 Setup & Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/AnupDangi/VyaparAI.git
    cd VyaparAI
    ```

2.  **Backend Setup**
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    python main.py
    ```
    *Create a `.env` file in `backend/` with configs for DATABASE_URL,
    DATABASE_URL=
    CLOUDINARY_API_SECRET=
    CLOUDINARY_API_KEY=
    GROQ_API_KEY=
    QDRANT_API_KEY=
    QDRANT_URL=
*

3.  **Frontend Setup**
    ```bash
    cd vyaparai-commerce-platform
    npm install
    npm run dev
    ```
    *Create a `.env` file in `vyaparai-commerce-platform/` with `VITE_API_URL` and `VITE_CLERK_PUBLISHABLE_KEY`.*

## 🚀 Deployment

The project includes a `render.yaml` for easy deployment of the backend.
1. push code to GitHub.
2. Connect your repo to Render.
3. Select "Blueprints" or "Web Service".
4. If manually configuring:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python main.py`
