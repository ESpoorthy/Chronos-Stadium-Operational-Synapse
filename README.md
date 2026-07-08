# Chronos Stadium AI

> "The world's first Generative Future Engine for Mega Events."

![Architecture Preview](https://via.placeholder.com/1200x600/050816/4F8CFF?text=Chronos+Stadium+AI+-+System+Architecture)

Traditional stadium systems monitor the present. Chronos predicts multiple possible futures. It continuously generates hundreds of possible operational scenarios from live stadium data, evaluates them using AI reasoning, explains the consequences, and recommends the best operational decisions before problems occur.

---

## ⚡ Core Features

- **Future Simulation Engine**: Generates 100+ possible futures continuously using Gemini 2.5 Flash and LangGraph.
- **Proactive AI Decision Engine**: Ranks futures by probability and risk, recommending actionable operational decisions.
- **Live Intelligence Dashboard**: Real-time integration of crowd density, weather, transit, and stadium sensors.
- **Generative Scenario Generator**: Natural language query engine ("What if the match goes to penalties?").
- **Multi-Agent Orchestration**: Specialized LangGraph agents for Crowd, Transit, Weather, Food, and Emergency operations.
- **Interactive Stadium Map**: Live visualization of stadium gates and transit hubs using React Flow.
- **Dynamic Theme Engine**: Seamless transitioning between Dark Futuristic Mode and Clean Light Mode.


## 🏗 Technology Stack

- **Frontend**: Next.js 15, React 19, TypeScript, TailwindCSS, shadcn/ui, Framer Motion.
- **Backend**: FastAPI, Python 3.12, SQLAlchemy (Async), Alembic, Pydantic v2.
- **AI & Reasoning**: LangGraph, LangChain, Gemini 2.5 Flash, FAISS.
- **Data & Cache**: PostgreSQL, Redis.
- **Deployment**: Docker, Docker Compose.

---

## 📂 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph multi-agent logic
│   │   ├── database/        # Async SQLAlchemy setup
│   │   ├── models/          # DB Models (Users, Sensors, Predictions)
│   │   ├── routers/         # FastAPI endpoints
│   │   ├── schemas/         # Pydantic schemas
│   │   └── simulation/      # Mock live data generators
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   │   ├── dashboard/
│   │   │   ├── scenarios/
│   │   │   └── ...
│   │   ├── components/      # UI components (shadcn/ui, Recharts)
│   │   └── lib/
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Installation & Deployment

### 1. Prerequisites
- Node.js 20+ (for frontend)
- Python 3.12 (for backend)
- (Optional) Docker & Docker Compose for full-stack orchestration

### 2. Environment Variables
Copy the example environment file and fill in your details:
```bash
cp .env.example .env
```
Ensure you provide a valid `GEMINI_API_KEY`.

### 3. Running Locally (Without Docker)

**Start the Frontend:**
```bash
cd frontend
npm install
npm run dev
```
*Frontend will be available at http://localhost:3000*

**Start the Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head # To run migrations
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend API will be available at http://localhost:8000*

### 4. Running with Docker Compose
To deploy the entire stack (Postgres, Redis, Backend API, Next.js Frontend) using Docker:

```bash
docker-compose up --build
```

---

## 🧠 The AI Workflow (Future Engine)

1. **State Ingestion**: Live telemetry (crowd, weather, transit) is ingested via FastAPI and cached in Redis.
2. **Planner Agent**: Analyzes current stadium anomalies (e.g. 70% rain probability, Gate C congestion).
3. **Sub-Agents Evaluation**: LangGraph routes context to specialized agents (Weather Agent, Transit Agent, Crowd Agent).
4. **Future Generation**: Gemini 2.5 Flash synthesizes agent reports and generates 100 simulated timelines.
5. **Ranking & Output**: Futures are ranked by probability/risk. The top 5 are returned with specific operational recommendations (e.g., "Deploy volunteers to Gate D").

---

*Designed for enterprise-scale mega events. Built with production-grade architecture.*
