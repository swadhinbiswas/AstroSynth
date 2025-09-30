# AstroSynth Architecture

## System overview

```mermaid
graph TB
    subgraph Client["🖥️ Client Layer"]
        UI["Next.js 15 · React 19<br/>App Router · Tailwind"]
        R3F["Three.js / R3F<br/>Live 3D Planet"]
        RQ["TanStack Query<br/>+ Zustand store"]
    end

    subgraph API["⚡ API Layer — FastAPI"]
        MW["Middleware<br/>CORS · Rate limit · Audit"]
        EP["Endpoints<br/>/predict /batch-predict /missions<br/>/datasets /leaderboard /metrics /feedback"]
        SEC["Security<br/>JWT · RBAC · Pydantic validation"]
    end

    subgraph ML["🧠 ML Layer"]
        PRED["Predictor<br/>artifact loader"]
        SHAP["Explainability<br/>SHAP + fallback"]
        ART[("Model artifacts<br/>*.joblib + registry.json")]
    end

    subgraph DATA["🗄️ Data Layer"]
        PG[("PostgreSQL 16<br/>8 tables")]
        ALEM["Alembic migrations"]
        OBJ[("S3-compatible<br/>object storage")]
    end

    subgraph OPS["📊 Observability"]
        PROM["Prometheus"]
        GRAF["Grafana"]
    end

    UI --> RQ --> MW --> EP
    R3F -.reads params.-> UI
    EP --> SEC
    EP --> PRED --> ART
    PRED --> SHAP
    EP --> PG
    ALEM --> PG
    EP -.datasets.-> OBJ
    EP --> PROM --> GRAF
```

## Request flow — `POST /api/v1/predict`

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant F as Next.js Frontend
    participant A as FastAPI
    participant P as Predictor
    participant E as SHAP Service
    participant D as PostgreSQL

    U->>F: Adjust sliders (radius, temp, period)
    F->>F: 3D planet recolours live (Three.js)
    U->>F: Click "Classify"
    F->>A: POST /predict {10 physics features}
    A->>A: Pydantic validation (ranges, types)
    A->>A: Rate limit check (60/min/IP)
    A->>P: predict_proba(features)
    P->>P: Build 14-feature vector (10 base + 4 derived)
    P-->>A: class + confidence + probabilities
    A->>E: explain_local(features)
    E-->>A: SHAP values per feature + waterfall
    A->>D: Persist prediction + explanations
    A-->>F: {predicted_class, confidence, probabilities, explanations}
    F->>F: Recolour planet atmosphere by verdict
    F-->>U: Verdict badge + probability bars + SHAP ranking
```

## Machine learning pipeline

```mermaid
graph LR
    A["1 · Ingestion<br/>NASA Exoplanet Archive<br/>Kepler / K2 / TESS"] --> B["2 · Validation<br/>range checks<br/>schema"]
    B --> C["3 · Cleaning<br/>median imputation<br/>bound clipping"]
    C --> D["4 · Feature engineering<br/>10 base + 4 derived<br/>physics features"]
    D --> E["5 · Train/test split<br/>stratified 80/20"]
    E --> F["6 · Hyperparameter opt<br/>Optuna · 30 trials"]
    F --> G["7 · Training<br/>RF · XGBoost<br/>LightGBM · CatBoost"]
    G --> H["8 · Evaluation<br/>acc · prec · rec<br/>F1 · ROC-AUC"]
    H --> I["9 · Explainability<br/>SHAP global + local"]
    I --> J["10 · Registry<br/>artifacts + metrics<br/>versioned"]
    J --> K["Deployment<br/>FastAPI serves artifact"]

    style A fill:#1e1b4b,stroke:#6d28d9,color:#fff
    style G fill:#1e1b4b,stroke:#a855f7,color:#fff
    style I fill:#1e1b4b,stroke:#22d3ee,color:#fff
    style K fill:#064e3b,stroke:#34d399,color:#fff
```

## Feature engineering — 10 base + 4 derived

| # | Feature | Unit | Physical meaning |
|---|---|---|---|
| 1 | `orbital_period` | days | Time for one orbit |
| 2 | `transit_duration` | hours | How long the planet blocks the star |
| 3 | `planet_radius` | R⊕ | Planet size |
| 4 | `stellar_radius` | R☉ | Host star size |
| 5 | `stellar_mass` | M☉ | Host star mass |
| 6 | `stellar_temp` | K | Stellar effective temperature |
| 7 | `transit_depth` | ppm | Fractional dimming |
| 8 | `snr` | — | Signal-to-noise ratio |
| 9 | `semi_major_axis` | AU | Orbital distance |
| 10 | `equilibrium_temp` | K | Planet temperature |

| Derived | Formula | What it captures |
|---|---|---|
| `snr_per_depth` | `snr / (depth + 1)` | Signal quality per unit dimming |
| `log_period` | `log1p(period)` | Compresses wide period range |
| `radius_ratio` | `R_p / (R★ × 109.2)` | True planet-to-star size ratio |
| `temp_ratio` | `T_eq / T★` | Insolation balance |

## Database schema

```mermaid
erDiagram
    users ||--o{ predictions : makes
    users ||--o{ experiments : runs
    users ||--o{ reports : writes
    models ||--o{ predictions : serves
    predictions ||--o{ feedback : receives
    datasets ||--o{ experiments : feeds

    users {
        uuid id PK
        string email UK
        string password_hash
        string role "admin|scientist|viewer"
    }
    datasets {
        uuid id PK
        string mission "kepler|k2|tess"
        string version
        int rows_count
        string storage_uri
    }
    models {
        uuid id PK
        string name
        string algorithm
        jsonb metrics
        bool is_active
    }
    predictions {
        uuid id PK
        jsonb input_features
        string predicted_class
        float confidence "0..1"
        jsonb probabilities
        jsonb explanations
    }
    experiments {
        uuid id PK
        string name
        jsonb config
        jsonb results
    }
    reports {
        uuid id PK
        string title
        text content_md
    }
    feedback {
        uuid id PK
        string user_label
        text comment
    }
    audit_logs {
        int id PK
        string actor
        string action
        string resource
    }
```

## Deployment topology

```mermaid
graph TB
    subgraph Docker["docker compose"]
        FE["frontend<br/>Next.js :3000"]
        BE["backend<br/>FastAPI :8000"]
        PG[("postgres<br/>:5432")]
        MI[("minio<br/>:9000")]
        PR["prometheus<br/>:9090"]
        GR["grafana<br/>:3001"]
    end
    USER["🌍 User browser"] --> FE
    FE --> BE
    BE --> PG
    BE --> MI
    PR -.scrapes /metrics-prom.-> BE
    GR --> PR
```

## Technology decisions

| Choice | Why |
|---|---|
| **FastAPI** | Native async, Pydantic v2 validation, auto OpenAPI docs judges can click |
| **Artifact-based serving** | Model never trains on request → <300ms p50, fully reproducible |
| **SHAP with deterministic fallback** | Explanations always available; API never 500s on explainability |
| **Procedural planet textures** | Zero external assets → works offline, no CDN/licence issues |
| **14-feature parity train↔serve** | Same `features.py` logic mirrored in `predictor.py`, verified by tests |
| **PostgreSQL + Alembic** | Schema is reviewable as SQL *and* migration-managed |
| **Prometheus/Grafana** | Judges can see the ops story, not just the ML story |

## Scaling path

| Today | At scale |
|---|---|
| In-memory rate limiter | Redis sliding window |
| Local `.joblib` artifacts | S3 + MLflow Model Registry (`MLFLOW_TRACKING_URI` already plumbed) |
| Synthetic training data | Live TAP queries to NASA Exoplanet Archive + caching layer |
| Synchronous batch predict | Celery/Arq queue with job polling |
| Single Postgres | Read replicas + partitioned `predictions` by month |
