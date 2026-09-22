# MatchAI — AI-Powered Client–Supplier Matchmaking Platform

> **Wisdom Group AI Intern Evaluation Project**  
> Submission deadline: Thursday, 24 September 2026, 4:00 PM

A full-stack web application that connects clients with suitable suppliers using an AI-powered semantic matching system built on Gemini embeddings and pgvector.

---

## Project Overview

MatchAI eliminates the manual effort of B2B procurement by automatically analysing client requirements and supplier offerings, then ranking the most compatible matches using a multi-factor AI scoring model.

**Phase 1** (this submission): Complete CRUD data flow — form → FastAPI → Supabase → dashboard.  
**Phase 2** (planned): AI matching engine with Gemini Embedding 2 + pgvector cosine similarity.

---

## Features

| Feature | Status |
|---|---|
| Client Requirement Portal | ✅ Complete |
| Supplier Offering Portal | ✅ Complete |
| Real-time Dashboard | ✅ Complete |
| REST API with Pydantic validation | ✅ Complete |
| Supabase PostgreSQL integration | ✅ Complete |
| Responsive B2B SaaS UI | ✅ Complete |
| Basic Tests (validation + scoring stubs) | ✅ Complete |
| AI Matching Engine (Gemini + pgvector) | 🔜 Phase 2 |
| Email Notifications | 🔜 Phase 2 |

---

## Architecture

```
┌─────────────────────────────────────────────┐
│           Browser (HTML/CSS/JS)             │
│  index.html · client.html · supplier.html   │
│  dashboard.html                             │
└─────────────────┬───────────────────────────┘
                  │  fetch("/api/...")
                  ▼
┌─────────────────────────────────────────────┐
│              FastAPI (Python)               │
│  app/api/clients.py   → POST/GET /api/clients   │
│  app/api/suppliers.py → POST/GET /api/suppliers │
│  app/api/matches.py   → GET /api/matches        │
│  app/api/notifications.py → GET /api/notifications │
│                                             │
│  app/services/database.py  ← all DB calls  │
│  app/services/embeddings.py ← Phase 2      │
│  app/services/matching.py  ← Phase 2       │
└─────────────────┬───────────────────────────┘
                  │  supabase-py SDK
                  ▼
┌─────────────────────────────────────────────┐
│         Supabase PostgreSQL                 │
│  public.clients       (BIGINT id)           │
│  public.suppliers     (BIGINT id)           │
│  public.matches       (empty in Phase 1)    │
│  public.notifications (empty in Phase 1)    │
│                                             │
│  pgvector extension (embeddings — Phase 2)  │
└─────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI 0.115, Uvicorn |
| Data validation | Pydantic v2 |
| Database | Supabase PostgreSQL |
| Vector DB | pgvector (via Supabase) |
| DB Client | supabase-py v2 |
| AI / Embeddings | Google Gemini Embedding 2 (Phase 2) |
| Frontend | Vanilla HTML5, CSS3, JavaScript (ES2022) |
| Testing | pytest, httpx |

---

## Database Schema

The application uses four tables in Supabase:

### `public.clients`
| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT | Auto-generated identity PK |
| `client_name` | TEXT | Required |
| `email` | TEXT | Required |
| `product_requirement` | TEXT | Required |
| `category` | TEXT | Required |
| `quantity_required` | NUMERIC | Required, > 0 |
| `unit` | TEXT | Required |
| `budget` | NUMERIC | Required, ≥ 0 |
| `location` | TEXT | Required |
| `city` | TEXT | Required |
| `state` | TEXT | Required |
| `country` | TEXT | Required |
| `delivery_timeline` | TEXT | Required |
| `delivery_days` | INTEGER | Required, > 0 |
| `additional_notes` | TEXT | Optional |
| `specs` | TEXT | Optional |
| `certifications` | TEXT | Optional |
| `embedding` | vector | NULL until Phase 2 |
| `created_at` | TIMESTAMPTZ | Auto |

### `public.suppliers`
| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT | Auto-generated identity PK |
| `supplier_name` | TEXT | Required |
| `email` | TEXT | Required |
| `product_offered` | TEXT | Required |
| `category` | TEXT | Required |
| `available_quantity` | NUMERIC | Required, ≥ 0 |
| `unit` | TEXT | Required |
| `pricing_details` | TEXT | Required |
| `unit_price` | NUMERIC | Required, ≥ 0 |
| `min_order_qty` | NUMERIC | Required, ≥ 0 |
| `location` | TEXT | Required |
| `city` | TEXT | Required |
| `state` | TEXT | Required |
| `country` | TEXT | Required |
| `delivery_capability` | TEXT | Required |
| `delivery_days` | INTEGER | Required, > 0 |
| `additional_notes` | TEXT | Optional |
| `specs` | TEXT | Optional |
| `certifications` | TEXT | Optional |
| `embedding` | vector | NULL until Phase 2 |
| `created_at` | TIMESTAMPTZ | Auto |

---

## Project Structure

```
client-supplier-matchmaking/
│
├── app/
│   ├── main.py              ← FastAPI app, routers, static mount
│   ├── config.py            ← Environment variable loader
│   │
│   ├── api/
│   │   ├── clients.py       ← POST/GET /api/clients
│   │   ├── suppliers.py     ← POST/GET /api/suppliers
│   │   ├── matches.py       ← GET /api/matches
│   │   └── notifications.py ← GET /api/notifications
│   │
│   ├── models/
│   │   ├── client.py        ← ClientCreate, ClientResponse
│   │   ├── supplier.py      ← SupplierCreate, SupplierResponse
│   │   └── match.py         ← MatchResponse, NotificationResponse
│   │
│   └── services/
│       ├── database.py      ← All Supabase operations
│       ├── embeddings.py    ← Gemini embedding (Phase 2 stub)
│       ├── matching.py      ← AI matching engine (Phase 2 stub)
│       └── notifications.py ← Notification service
│
├── frontend/
│   ├── index.html           ← Landing page
│   ├── client.html          ← Client requirement form
│   ├── supplier.html        ← Supplier offering form
│   ├── dashboard.html       ← Live dashboard
│   │
│   ├── css/
│   │   └── style.css        ← Full design system (B2B SaaS)
│   │
│   └── js/
│       ├── client.js        ← Client form validation + submit
│       ├── supplier.js      ← Supplier form validation + submit
│       └── dashboard.js     ← Dashboard data loading + rendering
│
├── tests/
│   ├── conftest.py          ← Pytest fixtures, sample payloads
│   ├── test_clients.py      ← Client API tests
│   ├── test_suppliers.py    ← Supplier API tests
│   └── test_matching.py     ← Scoring logic tests
│
├── .env                     ← Your credentials (never commit)
├── .env.example             ← Template for .env
├── .gitignore
├── requirements.txt
├── run.py                   ← python run.py to start server
└── README.md
```

---

## Setup

### 1. Clone and create virtual environment

```bash
git clone <repo-url>
cd client-supplier-matchmaking

python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-service-role-key
GEMINI_API_KEY=your-gemini-api-key
```

> **SUPABASE_KEY**: Use your **service role** key (Supabase Dashboard → Settings → API → service_role).  
> This key bypasses Row Level Security for server-side operations. Never expose it in frontend JS.

### 4. Create Supabase tables

Run the following SQL in your Supabase SQL Editor to create the `clients` and `suppliers` tables:

```sql
-- Clients table
CREATE TABLE IF NOT EXISTS public.clients (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    client_name         TEXT NOT NULL,
    email               TEXT NOT NULL,
    product_requirement TEXT NOT NULL,
    category            TEXT NOT NULL,
    quantity_required   NUMERIC(14,2) NOT NULL CHECK (quantity_required > 0),
    unit                TEXT NOT NULL,
    budget              NUMERIC(14,2) NOT NULL CHECK (budget >= 0),
    location            TEXT NOT NULL,
    city                TEXT NOT NULL,
    state               TEXT NOT NULL,
    country             TEXT NOT NULL,
    delivery_timeline   TEXT NOT NULL,
    delivery_days       INTEGER NOT NULL CHECK (delivery_days > 0),
    additional_notes    TEXT,
    specs               TEXT,
    certifications      TEXT,
    embedding           extensions.vector(768),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Suppliers table
CREATE TABLE IF NOT EXISTS public.suppliers (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    supplier_name       TEXT NOT NULL,
    email               TEXT NOT NULL,
    product_offered     TEXT NOT NULL,
    category            TEXT NOT NULL,
    available_quantity  NUMERIC(14,2) NOT NULL CHECK (available_quantity >= 0),
    unit                TEXT NOT NULL,
    pricing_details     TEXT NOT NULL,
    unit_price          NUMERIC(14,2) NOT NULL CHECK (unit_price >= 0),
    min_order_qty       NUMERIC(14,2) NOT NULL CHECK (min_order_qty >= 0),
    location            TEXT NOT NULL,
    city                TEXT NOT NULL,
    state               TEXT NOT NULL,
    country             TEXT NOT NULL,
    delivery_capability TEXT NOT NULL,
    delivery_days       INTEGER NOT NULL CHECK (delivery_days > 0),
    additional_notes    TEXT,
    specs               TEXT,
    certifications      TEXT,
    embedding           extensions.vector(768),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Matches table (populated by Phase 2 AI matching)
CREATE TABLE IF NOT EXISTS public.matches (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    client_id       BIGINT REFERENCES public.clients(id) ON DELETE CASCADE,
    supplier_id     BIGINT REFERENCES public.suppliers(id) ON DELETE CASCADE,
    final_score     NUMERIC(5,2),
    semantic_score  NUMERIC(5,2),
    category_score  NUMERIC(5,2),
    quantity_score  NUMERIC(5,2),
    budget_score    NUMERIC(5,2),
    location_score  NUMERIC(5,2),
    delivery_score  NUMERIC(5,2),
    rank            INTEGER,
    status          TEXT DEFAULT 'pending',
    explanation     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Notifications table (populated by Phase 2)
CREATE TABLE IF NOT EXISTS public.notifications (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    match_id            BIGINT REFERENCES public.matches(id) ON DELETE CASCADE,
    notification_type   TEXT NOT NULL,
    title               TEXT NOT NULL,
    message             TEXT NOT NULL,
    is_read             BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 5. Start the server

```bash
python run.py
```

Or directly with uvicorn:

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Landing page |
| `GET` | `/client` | Client portal |
| `GET` | `/supplier` | Supplier portal |
| `GET` | `/dashboard` | Dashboard |
| `POST` | `/api/clients` | Submit client requirement |
| `GET` | `/api/clients` | List all client requirements |
| `GET` | `/api/clients/{id}` | Get single client requirement |
| `POST` | `/api/suppliers` | Submit supplier offering |
| `GET` | `/api/suppliers` | List all supplier offerings |
| `GET` | `/api/suppliers/{id}` | Get single supplier offering |
| `GET` | `/api/matches` | List AI-generated matches |
| `GET` | `/api/notifications` | List notifications |
| `GET` | `/api/docs` | Interactive Swagger UI |
| `GET` | `/api/redoc` | ReDoc API documentation |

---

## Running Tests

```bash
pytest tests/ -v
```

Tests use mocked Supabase calls — no real database connection needed.

---

## AI Matching Approach (Phase 2 Plan)

The Phase 2 matching pipeline will:

1. **Embedding Generation**: Use `gemini-embedding-exp-03-07` (via `google-genai` SDK) to generate 768-dimension semantic vectors for each client requirement and supplier offering.

2. **Vector Search**: Use pgvector's `<=>` cosine distance operator to find the top-N semantically similar suppliers for each client requirement.

3. **Hard Gate Filters**: Before scoring, apply hard gates:
   - Supplier `available_quantity` ≥ client `quantity_required`
   - Supplier `unit_price × quantity` ≤ client `budget`
   - Supplier `delivery_days` ≤ client `delivery_days`
   - Category compatibility check

4. **Multi-Factor Scoring**: Compute a weighted composite score:
   ```
   final_score = (
     0.30 × semantic_score  +
     0.20 × category_score  +
     0.20 × budget_score    +
     0.15 × quantity_score  +
     0.10 × delivery_score  +
     0.05 × location_score
   )
   ```

5. **Storage**: Persist top matches to `public.matches` with rank and explanation.

6. **Notifications**: Create entries in `public.notifications` for matched clients and suppliers.

---

## Example Data Flow

```
POST /api/clients
Content-Type: application/json

{
  "client_name": "Acme Manufacturing",
  "email": "procurement@acme.com",
  "product_requirement": "High-grade stainless steel sheets for pressure vessels",
  "category": "Raw Materials",
  "quantity_required": 500,
  "unit": "Kilograms (kg)",
  "budget": 50000,
  "location": "Industrial Zone, Andheri East",
  "city": "Mumbai",
  "state": "Maharashtra",
  "country": "India",
  "delivery_timeline": "Within 3 weeks",
  "delivery_days": 21
}

→ 201 Created
{
  "id": 1,
  "client_name": "Acme Manufacturing",
  ...
  "created_at": "2026-09-22T08:00:00+05:30"
}
```

---

## Future Scalability

- **Authentication**: Supabase Auth + Row Level Security policies (already defined in schema) for multi-tenant isolation
- **Background jobs**: FastAPI BackgroundTasks or Celery for async matching pipeline
- **Webhooks**: Notify external systems when matches are generated
- **Analytics**: Match acceptance rates, category trends, geographic heatmaps
- **Batch matching**: Re-run matching when new suppliers register
- **Re-ranking**: Human feedback loop to improve match quality over time
- **Export**: CSV/PDF export of match reports

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SUPABASE_URL` | ✅ | Supabase project URL |
| `SUPABASE_KEY` | ✅ | Supabase service role key (server-side only) |
| `GEMINI_API_KEY` | Phase 2 | Google AI API key for embeddings |

---

*Built with FastAPI · Supabase · pgvector · Gemini AI · Vanilla JS*

