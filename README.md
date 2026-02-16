# 🚀 Text-to-SQL System with Ollama SQLCoder

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

---

## 📋 Overview

A powerful **Text-to-SQL system** that converts natural language queries into SQL using **Ollama's SQLCoder model**.

The system dynamically analyzes any connected database schema, generates accurate SQL queries, executes them, and returns real results instantly.

---

## ✨ Features

- 🔌 **Multi-Database Support** – PostgreSQL, MySQL, SQLite, SQL Server  
- 📊 **Dynamic Schema Analysis**
- 🤖 **AI-Powered SQL Generation**
- ⚡ **Automatic Query Execution**
- 📚 **Query History**
- 💡 **SQL Explanation**
- ⭐ **Saved Queries**
- 📤 **Export Results (CSV, JSON, SQL)**
- 🔍 **Schema Explorer**
- 📈 **Query Statistics**

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   React UI  │────▶│   FastAPI    │────▶│   Ollama    │
│  (Port 3000)│     │  (Port 8000) │     │  SQLCoder   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Database   │
                    │(PostgreSQL/ │
                    │ MySQL/SQLite│
                    └─────────────┘
```

---

# 🚀 Quick Start

## 📦 Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- Ollama

---

## 🐳 Using Docker (Recommended)

### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/text-to-sql.git
cd text-to-sql
```

### 2️⃣ Create Environment File

```bash
cp .env.example .env
```

### 3️⃣ Build and Start Containers

```bash
docker-compose up --build
```

### 4️⃣ Pull SQLCoder Model

```bash
docker-compose exec ollama ollama pull sqlcoder:latest
```

### 5️⃣ Access Application

Frontend: http://localhost:3000  
Backend API: http://localhost:8000  
API Docs: http://localhost:8000/docs  

---

# 🧑‍💻 Local Development

## 🔧 Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🎨 Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

# 📁 Project Structure

```
text-to-sql/
├── backend/
│   ├── main.py
│   ├── models/
│   │   └── sql_models.py
│   ├── services/
│   │   ├── sql_generator.py
│   │   └── sql_explainer.py
│   ├── database/
│   │   └── connection.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── QueryInput.tsx
│   │   │   ├── SqlOutput.tsx
│   │   │   ├── ResultsTable.tsx
│   │   │   ├── DatabaseConnection.tsx
│   │   │   └── ...
│   │   ├── hooks/
│   │   │   └── useTextToSql.ts
│   │   ├── pages/
│   │   │   └── index.tsx
│   │   └── App.tsx
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml
├── .env.example
├── init.sql
└── README.md
```

---

# 🔧 Configuration

Create a `.env` file:

```env
# Frontend
VITE_API_BASE_URL=http://localhost:8000

# Backend
OLLAMA_HOST=http://ollama:11434
DATABASE_URL=postgresql://postgres:password@postgres:5432/text2sql

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=text2sql

# MySQL
MYSQL_ROOT_PASSWORD=password
MYSQL_DATABASE=text2sql
MYSQL_USER=user
MYSQL_PASSWORD=password
```

---

# 🗄️ Database Setup

## PostgreSQL

```sql
psql -U postgres -h localhost -p 5432
CREATE DATABASE your_database;
```

## MySQL

```sql
mysql -u root -p -h localhost -P 3306
CREATE DATABASE your_database;
```

## SQLite

```bash
sqlite3 your_database.db
```

---

# 🧪 Load Sample Dataset

```bash
# PostgreSQL
psql -U postgres -d your_database -f init.sql

# MySQL
mysql -u root -p your_database < init.sql

# SQLite
sqlite3 your_database.db < init.sql
```

---

# 🎯 Usage Guide

### 1️⃣ Connect to Database
- Click database icon (🛢️)
- Enter credentials
- Click **Connect**

### 2️⃣ Ask Questions
Examples:
- "Show me all users"
- "Find top 5 products by revenue"
- "Count orders grouped by status"
- "List employees with salary above average"
- "Show customers who made purchases last month"

### 3️⃣ View Results
- Generated SQL shown in formatted box
- Results displayed in sortable table
- Export as CSV, JSON, or SQL

---

# 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/connect | POST | Connect to database |
| /api/disconnect | POST | Disconnect |
| /api/schema | GET | Get schema |
| /api/text-to-sql | POST | Convert text & execute |
| /api/explain | POST | Explain SQL |
| /api/history | GET | Query history |
| /api/health | GET | Health check |

---

# 🚢 Deployment

## Docker Production

```bash
docker-compose up -d --build
docker-compose logs -f
docker-compose down
```

## Manual Deployment

### Backend

```bash
cd backend
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app -b 0.0.0.0:8000
```

### Frontend

```bash
cd frontend
npm run build
npx serve -s dist -l 3000
```

---

# 🔍 Troubleshooting

### ❗ No Schema Provided
- Ensure database connection is active
- Verify credentials

### ❗ Ollama Not Running

```bash
curl http://localhost:11434/api/tags
ollama pull sqlcoder:latest
```

### ❗ Slow SQL Generation
- First query loads model
- Use smaller model: `sqlcoder:7b-q4_0`
- Enable caching

---

# 📊 Performance Optimization

- Cache schema
- Use connection pooling
- Add query caching
- Enable GPU acceleration

---

# 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push branch
5. Open Pull Request

