# Phase 5 — HireGraph AI Application Audit Report

**Date:** October 9, 2026  
**Project:** HireGraph AI  
**Research Title:** *"An Explainable AMRG-GraphSAGE Framework for Hiring Pattern Analysis under Evolving Job Requirements"*  
**System Architecture:**  
`React (Vite :3000) -> Spring Boot (:8081) -> PostgreSQL (:5432) & FastAPI (:8000) -> Frozen AMRG-GraphSAGE Model`

---

## 1. Executive Summary & Verification
The application ecosystem was audited end-to-end across all three architectural tiers (`frontend/`, `backend/`, and `ai_service/`), cross-referenced with PostgreSQL ground-truth counts, and validated against the frozen research checkpoints.

### Key Audit Findings:
1. **Tier Separation**:
   - The React frontend communicates **exclusively** with the Spring Boot API Gateway (`http://localhost:8081/api/v1`).
   - No direct communication exists between React and PostgreSQL or FastAPI.
   - All database credentials and model file paths remain strictly isolated on the backend.
2. **Database Integrity**:
   - PostgreSQL 18 on port 5432 contains the exact dataset:
     - 4,000 applications (2,200 Selected, 1,800 Rejected)
     - 1,534 students
     - 125 companies
     - 300 jobs
     - 18 skills
     - 7,656 student-skill associations (`HAS_SKILL`)
     - 1,566 job-skill associations (`REQUIRES_SKILL`)
     - Temporal cycles: 2023 (614) + 2024 (980) = 1,594 (Train), 2025 (1,160, Val), 2026 (1,246, Test)
3. **AI Inference Service**:
   - FastAPI loads the frozen production checkpoint `AMRG_GraphSAGE_model.pt` once during startup via lifespan management.
   - Serialized preprocessor artifacts (`scaler.joblib`, `encoder.joblib`, `node_maps.json`, `relation_maps.json`) are loaded without re-fitting.
   - Exact PyG graph ($N = 5,977$, $E = 43,044$, Relations $= 12$, Features $= 82$) is constructed and cached in memory.
4. **Spring Boot Backend**:
   - Runs on port 8081 (leaving port 8080 unblocked for Jenkins).
   - Manages all relational data, caching, and calls FastAPI for live GNN predictions.
   - Persists predictions into the `predictions` table with probability, predicted status, model name, and timestamp.
5. **Identified Gap to Address in Phase 5**:
   - `POST /api/v1/applications/predict/batch` endpoint is implemented in FastAPI and `AiServiceClient`, but needed in `ApplicationController` and `PredictionService`.

---

## 2. Frontend Architecture (`frontend/`)

### 2.1 Entry Point & Setup
- **Root Directory:** `frontend/`
- **Main Entry Point:** `frontend/src/main.tsx` -> `frontend/src/App.tsx`
- **Build Tool:** Vite + React 18 + TypeScript
- **Styling:** Vanilla CSS design system (`frontend/src/styles/index.css`) with curated Slate/Indigo/Emerald color tokens, glassmorphism, responsive navigation drawer, and accessible typography.
- **Port:** Port 3000 (`http://localhost:3000`)
- **Environment:** `frontend/.env` configuring `VITE_API_BASE_URL=http://localhost:8081/api/v1`

### 2.2 Routes & Pages
Configured via `frontend/src/routes/index.tsx`:
- `/dashboard` -> `DashboardPage` (Real metrics: 4000 apps, 1534 students, 125 companies, 300 jobs, 18 skills, 2200 selected, 1800 rejected; charts)
- `/candidates` -> `CandidatesPage` (Search, pagination, filters)
- `/candidates/:id` -> `CandidateDetailPage` (Student profile, skills, applications, historical outcomes)
- `/companies` -> `CompaniesPage` (Company catalog, industries, size, selection rates)
- `/companies/:id` -> `CompanyDetailPage` (Company statistics, jobs, applicant distributions)
- `/jobs` -> `JobsPage` (Job listings, domain filter, salary, required skills)
- `/jobs/:id` -> `JobDetailPage` (Job description, required skills, applicants)
- `/skills` -> `SkillsPage` (Skill demand vs. supply, student count, job requirement frequency)
- `/applications` -> `ApplicationsPage` (Application table, cycle filter, status filter, pagination)
- `/applications/:id` -> `ApplicationDetailPage` (Detailed application view, Candidate-Job Profile Comparison, Live "Run Prediction" button, Model Estimate display)
- `/graph` -> `KnowledgeGraphPage` (Cytoscape.js interactive visualization with 5,977 nodes overview, search, and 1-hop subgraphs)
- `/trends` -> `HiringTrendsPage` (Evolving requirements across 2023, 2024, 2025, 2026 cycles)
- `/model` -> `ModelResearchPage` (Research comparison of Standard GraphSAGE vs. AMRG-GraphSAGE, ablation findings)
- `*` -> `NotFoundPage` (Clean 404 handler with redirection)

### 2.3 API Client Layer
- `frontend/src/api/client.ts`: Axios instance configured with `http://localhost:8081/api/v1`, 15-second timeout, error interceptors translating HTTP status codes into user-friendly messages.
- Domain API clients:
  - `applications.ts`: `getApplications`, `getApplicationById`, `predictApplication`
  - `candidates.ts`: `getCandidates`, `getCandidateById`
  - `companies.ts`: `getCompanies`, `getCompanyById`
  - `dashboard.ts`: `getDashboardSummary`
  - `graph.ts`: `getGraphOverview`, `getSubgraph`
  - `jobs.ts`: `getJobs`, `getJobById`
  - `model.ts`: `getModelBenchmarks`, `getModelMetadata`
  - `skills.ts`: `getAllSkills`, `getSkillDemand`
  - `trends.ts`: `getHiringTrends`

---

## 3. Backend Architecture (`backend/`)

### 3.1 Framework & Configuration
- **Framework:** Spring Boot 3.2.3 with Java 17 / 21
- **Port:** 8081 (`server.port: 8081`)
- **Database Connection:** PostgreSQL at `jdbc:postgresql://localhost:5432/hiregraph_db` (Flyway migrations enabled)
- **AI Service Client:** Spring WebClient targeting `http://localhost:8000` with 15-second response timeout

### 3.2 Spring Controllers
All exposed under `/api/v1`:
- `DashboardController`: `GET /api/v1/dashboard/summary`
- `CandidateController`: `GET /api/v1/candidates`, `GET /api/v1/candidates/{studentId}`
- `CompanyController`: `GET /api/v1/companies`, `GET /api/v1/companies/{companyId}`
- `JobController`: `GET /api/v1/jobs`, `GET /api/v1/jobs/{jobId}`
- `SkillController`: `GET /api/v1/skills`, `GET /api/v1/skills/demand`
- `ApplicationController`:
  - `GET /api/v1/applications`
  - `GET /api/v1/applications/{applicationId}`
  - `POST /api/v1/applications/{applicationId}/predict`
- `GraphController`: `GET /api/v1/graph/overview`, `GET /api/v1/graph/subgraph/{type}/{id}`
- `AnalyticsController`: `GET /api/v1/analytics/trends`
- `ModelController`: `GET /api/v1/model/benchmarks`, `GET /api/v1/model/metadata`
- `IngestionController`: `POST /api/v1/admin/ingest` (administrative endpoint)

### 3.3 Domain Entities & Repositories
Mapped to PostgreSQL relational tables:
- `Student` (`students` table)
- `Company` (`companies` table)
- `Job` (`jobs` table)
- `Skill` (`skills` table)
- `StudentSkill` (`student_skills` table)
- `JobSkill` (`job_skills` table)
- `Application` (`applications` table)
- `Prediction` (`predictions` table with unique constraint on `application_id`, `model_name`, `model_version`)
- `ModelBenchmark` (`model_benchmarks` table)

---

## 4. AI Inference Service (`ai_service/`)

### 4.1 Implementation & Lifecycle
- **Framework:** Python FastAPI (`ai_service/app/main.py`)
- **Host & Port:** `0.0.0.0:8000`
- **Lifespan Startup:**
  - Loads serialized preprocessing artifacts (`ai_service/artifacts/`)
  - Constructs the full PyG `Data` graph ($N = 5,977$, $E = 43,044$)
  - Instantiates `AMRGGraphSAGE(in_channels=82, hidden_channels=128, num_relations=12, num_layers=2, dropout=0.20)`
  - Loads frozen weights from `Codebase/AMRG_GraphSAGE_model.pt`
  - Sets model to evaluation mode (`model.eval()`)

### 4.2 Endpoints Exposed
- `GET /health`: Engine status, node count, edge count, feature dimension
- `GET /model/metadata`: Verified research benchmark metrics, graph dimensions, temporal split details
- `POST /predict/application/{application_id}`: Single application inference
- `POST /predict/batch`: Multi-application inference
- `GET /graph/neighborhood/{type}/{id}`: 1-hop subgraph extraction

---

## 5. Golden Prediction Baseline Check
The following reference applications from the test split are verified against frozen research outputs:
- `A00001`: Estimated Probability $\approx 80.63\%$, Estimated Status = `SELECTED`
- `A00002`: Estimated Probability $\approx 13.23\%$, Estimated Status = `REJECTED`
- `A00003`: Estimated Probability $\approx 16.54\%$, Estimated Status = `REJECTED`
- `A00004`: Estimated Probability $\approx 83.81\%$, Estimated Status = `SELECTED`

---

## 6. Audit Action Items for Phase 5 Stabilization
1. **API Expansion**: Add `POST /api/v1/applications/predict/batch` endpoint in `ApplicationController` and `PredictionService`.
2. **Service Orchestration**: Ensure all three tiers (FastAPI :8000, Spring Boot :8081, Vite :3000) are started and responsive.
3. **Automated Testing**: Run unit and integration tests across Python, Java, and TypeScript builds.
4. **Browser End-to-End Walkthrough**: Execute the 9-step golden demonstration flow using the browser subagent.
