# 🏛️ CIVIC LENS

**An Advanced Financial Intelligence Suite for Kenyan Political Campaign Finance**

CIVIC LENS visualises donation networks, traces funding influence, simulates policy regulations, and uses AI to explain campaign financial dependencies — revealing how money flows through Kenya's political ecosystem.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [Database Schema](#database-schema)
- [Key Modules](#key-modules)
- [Known Limitations](#known-limitations)

---

## Overview

CIVIC LENS is a full-stack web application that provides transparency into political campaign funding in Kenya. It ingests donation data from CSV files (or uploaded documents), builds a graph-based model of donor-candidate relationships, and exposes this data through interactive visualisations including:

- Bar charts of total funding raised per candidate
- Force-directed network graphs of donor-candidate connections
- Choropleth maps of county-level funding concentration
- A policy simulator that models the impact of hypothetical regulations
- An AI explainer powered by GPT-3.5-turbo that summarises funding patterns in English and Swahili

---

## Features

| Module | Description |
|--------|-------------|
| **Funding Trends** | Bar charts showing total campaign funds raised per candidate |
| **Network Intelligence Engine** | Interactive force-directed graph; edge weight = donation amount; Louvain community detection |
| **Geographic Influence Engine** | Choropleth map of Kenya counties with a Funding Concentration Index (FCI) |
| **Policy Simulator** | What-if engine for corporate bans, donation caps, and public funding scenarios |
| **AI Explainer Bot** | GPT-3.5-turbo analysis of per-candidate funding, with English and Swahili output |
| **Data Intake Pipeline** | Upload text documents; LLM extracts donation records and seeds the database |

---

## Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.x | Core language |
| FastAPI | 0.135.0 | REST API framework |
| SQLAlchemy | 2.0.47 | ORM |
| Alembic | 1.18.4 | Database migrations |
| PostgreSQL | any | Relational database |
| NetworkX | 3.6.1 | Graph construction and analysis |
| python-louvain | 0.16 | Community detection |
| GeoPandas | 1.1.2 | Geospatial data processing |
| Pandas | 3.0.1 | Data manipulation |
| LangChain | 1.2.10 | LLM orchestration |
| OpenAI (GPT-3.5-turbo) | 2.24.0 | AI explanations and data extraction |
| Uvicorn | 0.41.0 | ASGI server |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2.0 | UI framework |
| Vite | 7.3.1 | Build tool and dev server |
| React Router DOM | 7.13.1 | Client-side routing |
| D3.js | 7.9.0 | Low-level data visualisation |
| Recharts | 3.7.0 | Chart components |
| React Force Graph 2D | 1.29.1 | Interactive network graphs |
| Leaflet + React-Leaflet | 1.9.4 / 5.0.0 | Interactive maps |
| Tailwind CSS | 3.4.19 | Utility-first styling |
| Axios | 1.13.6 | HTTP client |

---

## Project Structure

```
CIVIC_LENS/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI application and all API endpoints
│   │   ├── models.py          # SQLAlchemy ORM models
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── database.py        # PostgreSQL connection and session factory
│   │   ├── seed.py            # Seeds the database from CSV files
│   │   └── routers/
│   │       ├── network.py     # Network graph generation router
│   │       └── geography.py   # Geographic influence router
│   ├── alembic/
│   │   ├── versions/
│   │   │   └── 19db4b07d623_master_init_for_phase_2.py
│   │   ├── env.py
│   │   └── alembic.ini
│   ├── data/
│   │   ├── Candidates.csv
│   │   ├── DONORS.csv
│   │   ├── DONATIONS.csv
│   │   ├── COUNTIES.csv
│   │   ├── ELECTION_CYCLE.csv
│   │   ├── SIMULATION_PARAMETERS.csv
│   │   └── kenya_counties.geojson
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Root component with routing and header
│   │   ├── main.jsx           # React entry point
│   │   ├── api.js             # API helper functions
│   │   ├── App.css
│   │   ├── index.css
│   │   └── components/
│   │       ├── DashboardHome.jsx    # Landing page with module cards
│   │       ├── FundingTrends.jsx    # Module 1: Bar charts
│   │       ├── NetworkGraph.jsx     # Module 2: Force-directed graph
│   │       ├── MapVisualization.jsx # Module 3: Choropleth map
│   │       ├── PolicySimulator.jsx  # Module 4: What-if engine
│   │       ├── AIExplainer.jsx      # Module 5: AI analysis
│   │       └── DataIntake.jsx       # Document upload pipeline
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── index.html
└── requirements.txt
```

---

## Prerequisites

- **Python 3.9+**
- **Node.js 18+** and **npm**
- **PostgreSQL** (running locally or accessible remotely)
- An **OpenAI API key** (required for the AI Explainer and Data Intake features)

---

## Installation

### Backend Setup

```bash
# 1. Navigate to the backend directory
cd backend

# 2. (Recommended) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Copy the example environment file and fill in your values
cp .env.example .env
```

### Frontend Setup

```bash
# Navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install
```

---

## Environment Variables

Create a `.env` file inside the `backend/` directory (copy from `.env.example`):

```env
# PostgreSQL connection string
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/civic_lens

# OpenAI API key (required for AI Explainer and Data Intake modules)
OPENAI_API_KEY=sk-...
```

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ Yes | Full PostgreSQL connection string |
| `OPENAI_API_KEY` | ✅ Yes (for AI features) | OpenAI secret key for GPT-3.5-turbo |

---

## Database Setup

1. **Create the PostgreSQL database:**

```sql
CREATE DATABASE civic_lens;
```

2. **Run Alembic migrations** to create all tables:

```bash
cd backend
alembic upgrade head
```

3. **Seed the database** with the bundled CSV data:

```bash
python -m app.seed
```

---

## Running the Application

### Start the Backend API

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive API docs (Swagger UI): `http://localhost:8000/docs`

### Start the Frontend Dev Server

```bash
cd frontend
npm run dev
```

The app will be available at `http://localhost:5173`.

### Frontend Build for Production

```bash
cd frontend
npm run build       # Outputs to frontend/dist/
npm run preview     # Preview the production build locally
```

### Linting

```bash
cd frontend
npm run lint        # ESLint check
```

---

## API Reference

Base URL: `http://localhost:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/candidates` | Returns a list of all candidates |
| `GET` | `/api/donors` | Returns a list of all donors |
| `GET` | `/api/network-metrics` | Returns a bipartite graph with centrality scores and Louvain community assignments |
| `GET` | `/api/geographic-influence` | Returns GeoJSON with Funding Concentration Index (FCI) per county |
| `GET` | `/api/ai-explainer/{candidate_id}` | Returns an AI-generated funding summary in English and Swahili for a specific candidate |
| `POST` | `/api/simulate-policy` | Simulates policy regulations and returns their impact on the funding network |
| `POST` | `/api/upload` | Accepts a text document, extracts donation data via LLM, and seeds the database |

### Example: Simulate Policy

**Request body:**
```json
{
  "ban_corporate": true,
  "donation_cap": 500000,
  "public_funding_boost": 0.2
}
```

**Response:** Updated network metrics reflecting the simulated constraints.

---

## Database Schema

### `candidates`
| Column | Type | Description |
|--------|------|-------------|
| `candidate_id` | VARCHAR (PK) | Unique candidate identifier |
| `name` | VARCHAR | Candidate's full name |
| `party` | VARCHAR | Political party |
| `office_sought` | VARCHAR | Position being contested |
| `county` | VARCHAR | County of candidacy |
| `election_year` | INTEGER | Year of the election |

### `donors`
| Column | Type | Description |
|--------|------|-------------|
| `donor_id` | VARCHAR (PK) | Unique donor identifier |
| `name` | VARCHAR | Donor name |
| `type` | VARCHAR | `Corporate` or `Individual` |
| `industry` | VARCHAR | Donor's industry sector |
| `home_county` | VARCHAR | Donor's county |
| `tier` | INTEGER | Donor tier (contribution level) |

### `donations`
| Column | Type | Description |
|--------|------|-------------|
| `donation_id` | INTEGER (PK) | Unique donation identifier |
| `donor_id` | VARCHAR (FK → donors) | Reference to donor |
| `candidate_id` | VARCHAR (FK → candidates) | Reference to candidate |
| `amount` | NUMERIC | Donation amount (KES) |
| `date` | DATE | Date of donation |
| `election_year` | INTEGER | Election cycle |

### `counties`
| Column | Type | Description |
|--------|------|-------------|
| `county_name` | VARCHAR (PK) | County name (matches GeoJSON) |
| `registered_voters` | INTEGER | Number of registered voters |

### `election_cycles`
| Column | Type | Description |
|--------|------|-------------|
| `election_year` | INTEGER (PK) | Available election cycle year |

### `simulation_parameters`
| Column | Type | Description |
|--------|------|-------------|
| `parameter` | VARCHAR (PK) | Parameter name |
| `default_value` | VARCHAR | Default value for the policy simulator |

---

## Key Modules

### Network Intelligence Engine (`/api/network-metrics`)
Builds a bipartite graph using **NetworkX** where donor nodes connect to candidate nodes weighted by donation amount. **Louvain community detection** (python-louvain) then identifies funding clusters. The response includes:
- Node list with `type`, `total_funding`, `degree_centrality`, and `community` labels
- Edge list with `source`, `target`, and `weight`

### Geographic Influence Engine (`/api/geographic-influence`)
Joins the donations table with `kenya_counties.geojson` via **GeoPandas**. Computes a **Funding Concentration Index** (FCI = county donations ÷ national total) for each of Kenya's 47 counties and returns the result as enriched GeoJSON for choropleth rendering with Leaflet.

### Policy Simulator (`/api/simulate-policy`)
Accepts policy parameters (corporate donor ban, per-donor cap, public funding injection) and recomputes the network graph under those constraints, returning a before/after comparison of candidate funding totals and network centrality.

### AI Explainer Bot (`/api/ai-explainer/{candidate_id}`)
Uses **LangChain** with **GPT-3.5-turbo** to generate a structured funding analysis for a given candidate. The prompt instructs the model to produce:
- Key funding metrics (total raised, top donors, sector breakdown)
- A risk assessment (concentration, corporate dependency)
- Full output in both **English** and **Swahili**

### Data Intake Pipeline (`/api/upload`)
Accepts an uploaded text file, passes its content to an LLM extraction prompt, and parses out structured donation records (donor name, amount, candidate, date). Extracted entities are written to the PostgreSQL sandbox database.

---

## Known Limitations

- **No authentication or authorisation** — all API endpoints are publicly accessible. CORS is set to allow all origins (`*`).
- **OpenAI dependency** — the AI Explainer and Data Intake modules require a valid `OPENAI_API_KEY`. Without it, those endpoints will fail.
- **Hardcoded API base URL** — the frontend points to `http://localhost:8000` by default. Update `frontend/src/api.js` for production deployments.
- **No test suite** — there are currently no automated tests in either the backend or frontend.
- **Schemas not enforced** — `backend/app/schemas.py` is present but empty; API request/response validation relies on the ORM models.
