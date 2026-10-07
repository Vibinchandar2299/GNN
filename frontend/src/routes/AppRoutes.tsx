import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { DashboardPage } from '../pages/Dashboard/DashboardPage';
import { CandidatesPage } from '../pages/Candidates/CandidatesPage';
import { CandidateDetailPage } from '../pages/Candidates/CandidateDetailPage';
import { CompaniesPage } from '../pages/Companies/CompaniesPage';
import { CompanyDetailPage } from '../pages/Companies/CompanyDetailPage';
import { JobsPage } from '../pages/Jobs/JobsPage';
import { JobDetailPage } from '../pages/Jobs/JobDetailPage';
import { SkillsPage } from '../pages/Skills/SkillsPage';
import { ApplicationsPage } from '../pages/Applications/ApplicationsPage';
import { ApplicationDetailPage } from '../pages/Applications/ApplicationDetailPage';
import { KnowledgeGraphPage } from '../pages/KnowledgeGraph/KnowledgeGraphPage';
import { HiringTrendsPage } from '../pages/HiringTrends/HiringTrendsPage';
import { ModelResearchPage } from '../pages/ModelResearch/ModelResearchPage';
import { NotFoundPage } from '../pages/NotFound/NotFoundPage';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="candidates" element={<CandidatesPage />} />
        <Route path="candidates/:studentId" element={<CandidateDetailPage />} />
        <Route path="companies" element={<CompaniesPage />} />
        <Route path="companies/:companyId" element={<CompanyDetailPage />} />
        <Route path="jobs" element={<JobsPage />} />
        <Route path="jobs/:jobId" element={<JobDetailPage />} />
        <Route path="skills" element={<SkillsPage />} />
        <Route path="applications" element={<ApplicationsPage />} />
        <Route path="applications/:applicationId" element={<ApplicationDetailPage />} />
        <Route path="graph" element={<KnowledgeGraphPage />} />
        <Route path="trends" element={<HiringTrendsPage />} />
        <Route path="model" element={<ModelResearchPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
};
