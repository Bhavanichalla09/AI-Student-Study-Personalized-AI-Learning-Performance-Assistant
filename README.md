# AI Student Study — Personalized AI Learning & Performance Assistant

An AI-powered personalized learning assistant designed to help students understand concepts, identify knowledge gaps, analyze mistakes, practice effectively, and track academic performance.

## 🎯 Project Goal

The system provides a personalized learning experience based on a student's:

- Concept mastery
- Quiz performance
- Mistakes
- Confidence levels
- Learning history
- Knowledge gaps

### Learning Cycle

**Assess → Diagnose → Recommend → Teach → Practice → Measure → Adapt**

---

## ✨ Key Features

- 📚 Personalized AI Study Assistance
- 🧠 Knowledge Gap Detection
- 🗺️ Knowledge Map
- 🎯 Diagnostic Practice Quizzes
- ❌ AI Mistake Analysis
- 💡 Personalized Remediation Recommendations
- 📝 Teach-Back Evaluation
- 📊 Learning History
- 📈 Performance Tracking
- 🤖 Google Gemini AI Integration
- 🗄️ Supabase PostgreSQL Database
- 🔐 Backend-based API architecture
- 🧪 Automated Testing

---

## 🛠️ Technology Stack

### Frontend
- Next.js
- TypeScript
- React
- Turbopack

### Backend
- Python
- FastAPI
- SQLAlchemy
- AsyncIO

### Database
- Supabase PostgreSQL
- AsyncPG

### AI
- Google Gemini API

### Testing
- Pytest

### Version Control
- Git
- GitHub

---

## 📂 Repository Structure

```text
AI-Student-Study-Personalized-AI-Learning-Performance-Assistant/
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── quiz/
│   │   │   ├── knowledge/
│   │   │   ├── history/
│   │   │   ├── curriculum/
│   │   │   └── ...
│   │   │
│   │   ├── components/
│   │   │   └── layout/
│   │   │
│   │   └── ...
│   │
│   ├── package.json
│   ├── next.config.ts
│   └── ...
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   └── ...
│   │
│   ├── tests/
│   │   └── conftest.py
│   │
│   ├── requirements.txt
│   └── ...
│
├── .gitignore
├── README.md
└── ...
