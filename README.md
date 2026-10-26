# VoiceMenu AI — Multilingual Voice-First Restaurant Food Ordering

VoiceMenu AI is a full-stack, multilingual, voice-first food ordering web application designed for restaurants. It solves the real-world communication barrier faced by travellers and customers who do not speak the local restaurant menu language.

Customers scan a table-specific QR code, converse naturally in their preferred language (Hindi, English, Tamil, or Telugu) with an AI dining assistant, discover unfamiliar dishes, customize items, and place orders through natural conversation or fallback text.

Powered by **Sarvam AI APIs** for Indian language Speech-to-Text (saaras:v4), conversational reasoning (sarvam-105b), text translation (sarvam-translate:v1), and Speech Synthesis (ulbul:v4-flash).

---

## Architecture & Technology Stack

- **Frontend**:
  - React 18+ with TypeScript (Strict mode, zero ny)
  - Vite 6 + Tailwind CSS (Mobile-first responsive UX)
  - React Router v6
  - Web Audio & MediaRecorder API (udio/webm;codecs=opus)
  - Vector QR code rendering (qrcode.react)
- **Backend**:
  - Python 3.11+
  - FastAPI with Pydantic v2 schemas
  - SQLite with SQLAlchemy 2.0 ORM
  - httpx async client for high-performance Sarvam API calls
- **AI Integrations (Sarvam AI)**:
  - **Speech-to-Text**: POST https://api.sarvam.ai/speech-to-text with saaras:v4 (mode=transcribe, multipart/form-data)
  - **Conversational Intelligence**: POST https://api.sarvam.ai/v1/chat/completions with sarvam-105b (easoning_effort: None for low-latency dialogue)
  - **Menu Translation**: POST https://api.sarvam.ai/translate with sarvam-translate:v1 backed by SQLite TranslationCache
  - **Text-to-Speech**: POST https://api.sarvam.ai/text-to-speech with ulbul:v4-flash
- **Security & Integrity**:
  - SARVAM_API_KEY stays exclusively on the server. Never exposed to browser bundles.
  - LLM never calculates authoritative prices or commits orders; the server-side Order Engine strictly validates availability, quantities, customizations, and prices.
  - Customer speech is treated as untrusted input.
  - Kitchen Display System (KDS) protected via PIN verification (X-Kitchen-Pin: 1234).

---

## Directory Structure

`
voicemenu-ai/
├── backend/
│   ├── app/
│   │   ├── config.py              # Environment configuration via pydantic-settings
│   │   ├── database.py            # SQLite engine, sessions, schema setup
│   │   ├── models.py              # SQLAlchemy ORM models
│   │   ├── schemas.py             # Pydantic v2 request & response schemas
│   │   ├── seed_menu.py           # Seed menu for South Spice Kitchen (~15 items)
│   │   ├── main.py                # FastAPI app entrypoint, CORS, exception handlers
│   │   ├── routers/
│   │   │   ├── menu.py            # Menu querying & item detail endpoints
│   │   │   ├── orders.py          # Draft order CRUD & confirmation
│   │   │   ├── voice.py           # Speech-to-text, converse, text-to-speech
│   │   │   ├── kitchen.py         # KDS orders feed & state transitions
│   │   │   └── qr.py              # Table QR code PNG generation
│   │   ├── services/
│   │   │   ├── order_engine.py    # Authoritative pricing & validation engine
│   │   │   ├── sarvam_stt.py      # Sarvam Saaras v4 STT
│   │   │   ├── sarvam_tts.py      # Sarvam Bulbul v4-flash TTS
│   │   │   ├── sarvam_translate.py# Sarvam Translation + DB cache
│   │   │   ├── sarvam_chat.py     # Sarvam 105B Chat Completion
│   │   │   └── conversation.py    # Conversation orchestration & fallback engine
│   │   └── utils/
│   │       └── audio.py           # Audio MIME type & file size validator (max 10MB)
│   ├── tests/
│   │   ├── test_api.py            # Route integration tests
│   │   └── test_order_engine.py   # Unit tests for order engine & fuzzy matching
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/client.ts          # Typed API client
│   │   ├── components/            # UI components (Menu, Cart, Mic, KDS, etc.)
│   │   ├── hooks/                 # useAudioRecorder, useConversation
│   │   ├── pages/                 # CustomerPage, KitchenDashboard, QRGenerator
│   │   ├── types/index.ts         # TypeScript interfaces & language constants
│   │   ├── App.tsx                # Client-side router
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── .gitignore
└── README.md
`

---

## Getting Started

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.11)
- **Node.js 18+** & 
pm
- **Sarvam AI API Key** from [indus.sarvam.ai](https://indus.sarvam.ai/key-management) (Optional for demo/fallback mode)

---

### 2. Backend Setup

`powershell
cd backend

# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env
`

Edit .env to configure your settings:
`env
SARVAM_API_KEY=your_actual_sarvam_api_key_here
KITCHEN_PIN=1234
DATABASE_URL=sqlite:///./voicemenu.db
CORS_ORIGINS=http://localhost:5173
`

Start the FastAPI backend server:
`powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
`
Interactive Swagger documentation is available at http://localhost:8000/docs.

---

### 3. Frontend Setup

In a separate terminal:
`powershell
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
`
The frontend will start at http://localhost:5173.

---

## User Flows & URLs

| Target | URL | Description |
|---|---|---|
| **Customer Table Ordering** | http://localhost:5173/r/demo-restaurant/table-1 | Customer scan destination for Table 1. Mobile-first ordering UI. |
| **Alternative Table** | http://localhost:5173/r/demo-restaurant/table-5 | Table 5 ordering interface. |
| **Kitchen Dashboard (KDS)** | http://localhost:5173/kitchen/demo-restaurant | Real-time kitchen orders board (PIN: 1234). Status transitions: Pending -> Accepted -> Preparing -> Ready -> Completed. |
| **QR Code Standee Generator** | http://localhost:5173/kitchen/demo-restaurant/qr | Generate and print high-resolution table QR codes. |
| **Demo Landing Page** | http://localhost:5173/ | Quick links to test customer tables and kitchen dashboard. |

---

## Seed Menu (South Spice Kitchen)

The demo menu includes 15 authentic dishes across 5 categories with localized Hindi, Tamil, and Telugu names, dietary flags, spice levels, and customization options:
- **Dosa**: Masala Dosa (₹120), Plain Dosa (₹80), Rava Dosa (₹110), Mysore Masala Dosa (₹140)
- **Idli**: Idli Sambar (₹70), Ghee Podi Idli (₹90)
- **Rice**: Curd Rice (₹100), Lemon Rice (₹110), Chicken Biryani (₹220)
- **Snacks**: Medu Vada (₹70), Samosa (₹60), Chicken 65 (₹180 — marked unavailable for testing)
- **Beverages**: South Indian Filter Coffee (₹50), Mango Lassi (₹80), Masala Chai (₹40)

---

## Running Automated Tests

Run the backend test suite:
`powershell
cd backend
python -m pytest tests/ -v
`

Tests cover:
- Menu querying, category filters, and veg-only flags
- Order calculation and fuzzy multilingual name matching
- Quantity constraints (positive integers, bounds checking)
- Customization option validation against allowed choices
- Out-of-stock item rejections
- Draft order modification (add, remove, update quantities)
- Explicit confirmation requirement and duplicate confirmation prevention
- Order status state transitions
- QR code generation endpoint
