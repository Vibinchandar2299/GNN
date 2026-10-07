-- ====================================================================
-- HireGraph AI - Flyway Database Migration V1
-- Target Database: PostgreSQL 18
-- ====================================================================

-- 1. STUDENTS
CREATE TABLE IF NOT EXISTS students (
    id BIGSERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    cgpa NUMERIC(4,2) NOT NULL,
    backlogs INTEGER NOT NULL,
    aptitude_score_pre NUMERIC(5,2) NOT NULL,
    coding_score_pre NUMERIC(5,2) NOT NULL,
    communication_score_pre NUMERIC(5,2) NOT NULL,
    projects_count INTEGER NOT NULL,
    internships_count INTEGER NOT NULL,
    certifications_count INTEGER NOT NULL,
    resume_score NUMERIC(5,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. COMPANIES
CREATE TABLE IF NOT EXISTS companies (
    id BIGSERIAL PRIMARY KEY,
    company_id VARCHAR(50) NOT NULL UNIQUE,
    company_name VARCHAR(150),
    industry VARCHAR(100) NOT NULL,
    company_size VARCHAR(50) NOT NULL,
    historical_selection_rate NUMERIC(6,4) NOT NULL,
    historical_average_selected_cgpa NUMERIC(4,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. JOBS
CREATE TABLE IF NOT EXISTS jobs (
    id BIGSERIAL PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL UNIQUE,
    job_title VARCHAR(150) NOT NULL,
    job_domain VARCHAR(100) NOT NULL,
    minimum_cgpa NUMERIC(4,2) NOT NULL,
    experience_required_months INTEGER NOT NULL,
    salary_lpa NUMERIC(5,2) NOT NULL,
    required_skill_count INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. SKILLS
CREATE TABLE IF NOT EXISTS skills (
    id BIGSERIAL PRIMARY KEY,
    skill_id VARCHAR(50) NOT NULL UNIQUE,
    skill_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 5. STUDENT_SKILLS
CREATE TABLE IF NOT EXISTS student_skills (
    id BIGSERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    skill_id VARCHAR(50) NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    skill_proficiency NUMERIC(4,2),
    CONSTRAINT uq_student_skill UNIQUE (student_id, skill_id)
);

-- 6. JOB_SKILLS
CREATE TABLE IF NOT EXISTS job_skills (
    id BIGSERIAL PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    skill_id VARCHAR(50) NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    required_skill_level NUMERIC(4,2),
    CONSTRAINT uq_job_skill UNIQUE (job_id, skill_id)
);

-- 7. APPLICATIONS
CREATE TABLE IF NOT EXISTS applications (
    id BIGSERIAL PRIMARY KEY,
    application_id VARCHAR(50) NOT NULL UNIQUE,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    company_id VARCHAR(50) NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    job_id VARCHAR(50) NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    cycle INTEGER NOT NULL,
    relevant_experience_months NUMERIC(5,2) NOT NULL,
    total_skill_count INTEGER NOT NULL,
    average_skill_proficiency NUMERIC(4,2) NOT NULL,
    role_shift_score NUMERIC(6,4) NOT NULL,
    skill_match_ratio NUMERIC(6,4) NOT NULL,
    required_skill_level_gap NUMERIC(6,4) NOT NULL,
    role_experience_match NUMERIC(6,4) NOT NULL,
    expected_hiring_count INTEGER NOT NULL,
    final_status INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 8. PREDICTIONS
CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    application_id VARCHAR(50) NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    predicted_probability NUMERIC(8,6) NOT NULL,
    predicted_status VARCHAR(20) NOT NULL,
    model_name VARCHAR(50) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_prediction_app_model UNIQUE (application_id, model_name, model_version)
);

-- 9. MODEL_BENCHMARKS
CREATE TABLE IF NOT EXISTS model_benchmarks (
    id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL UNIQUE,
    accuracy NUMERIC(6,4) NOT NULL,
    precision_score NUMERIC(6,4) NOT NULL,
    recall NUMERIC(6,4) NOT NULL,
    f1_score NUMERIC(6,4) NOT NULL,
    roc_auc NUMERIC(6,4) NOT NULL,
    dataset_description VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_students_student_id ON students(student_id);
CREATE INDEX IF NOT EXISTS idx_companies_company_id ON companies(company_id);
CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_skills_skill_id ON skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_applications_application_id ON applications(application_id);
CREATE INDEX IF NOT EXISTS idx_applications_student_id ON applications(student_id);
CREATE INDEX IF NOT EXISTS idx_applications_company_id ON applications(company_id);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_cycle ON applications(cycle);
CREATE INDEX IF NOT EXISTS idx_predictions_application_id ON predictions(application_id);

-- SEED VERIFIED RESEARCH BENCHMARKS
INSERT INTO model_benchmarks (model_name, accuracy, precision_score, recall, f1_score, roc_auc, dataset_description)
VALUES
    ('Standard GraphSAGE', 0.8387, 0.8443, 0.8699, 0.8569, 0.9140, 'Baseline GraphSAGE (uniform aggregation, 2 layers, 64 hidden channels)'),
    ('AMRG-GraphSAGE', 0.8427, 0.8493, 0.8714, 0.8602, 0.9142, 'Proposed Adaptive Multi-Relational GraphSAGE (12 relations, relation scoring, gating, multi-scale fusion)')
ON CONFLICT (model_name) DO NOTHING;
