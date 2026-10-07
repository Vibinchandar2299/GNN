import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Building2,
  Percent,
  GraduationCap,
  FileText,
  Network,
} from 'lucide-react';
import { companyApi } from '../../api/companyApi';
import { Company } from '../../types/company';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { MetricCard } from '../../components/common/MetricCard';
import { DisclaimerCard } from '../../components/common/DisclaimerCard';
import { formatNumber, formatPercent, formatDecimal } from '../../utils/formatting';

export const CompanyDetailPage: React.FC = () => {
  const { companyId } = useParams<{ companyId: string }>();
  const navigate = useNavigate();
  const [company, setCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCompany = async () => {
    if (!companyId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await companyApi.getCompanyById(companyId);
      setCompany(data);
    } catch (err: any) {
      setError(err.message || `Failed to fetch company profile for ${companyId}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompany();
  }, [companyId]);

  if (loading) {
    return <LoadingState message={`Retrieving company profile for ${companyId}...`} />;
  }

  if (error || !company) {
    return (
      <ErrorState
        title="Company Profile Not Found"
        message={error || `Could not find company with ID ${companyId}`}
        onRetry={fetchCompany}
      />
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button
          onClick={() => navigate('/companies')}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            color: 'var(--text-secondary)',
            fontSize: '0.88rem',
            cursor: 'pointer',
          }}
        >
          <ArrowLeft size={16} /> Back to Companies Directory
        </button>

        <button
          onClick={() => navigate(`/graph?type=company&id=${company.companyId}`)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'rgba(245, 158, 11, 0.15)',
            border: '1px solid rgba(245, 158, 11, 0.4)',
            color: '#fbbf24',
            fontSize: '0.85rem',
            fontWeight: 600,
          }}
        >
          <Network size={16} /> Explore Company Knowledge Subgraph
        </button>
      </div>

      <DisclaimerCard customText="Company hiring records and historical selection rates are extracted from the frozen multi-relational research placement dataset." />

      {/* Company Header */}
      <div
        className="card"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '20px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div
            style={{
              width: '56px',
              height: '56px',
              borderRadius: '12px',
              backgroundColor: 'rgba(245, 158, 11, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#f59e0b',
              border: '1px solid rgba(245, 158, 11, 0.4)',
            }}
          >
            <Building2 size={28} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>
                {company.companyName}
              </h2>
              <span
                style={{
                  padding: '2px 8px',
                  borderRadius: '4px',
                  backgroundColor: 'var(--bg-elevated)',
                  fontSize: '0.78rem',
                  fontFamily: 'var(--font-mono)',
                  color: '#f59e0b',
                }}
              >
                {company.companyId}
              </span>
            </div>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Industry Vertical: <strong style={{ color: 'var(--text-secondary)' }}>{company.industry}</strong> • Scale: {company.companySize}
            </p>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Historical Selection Rate</span>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--color-primary)', fontFamily: 'var(--font-mono)' }}>
            {formatPercent(company.historicalSelectionRate)}
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid-cols-3">
        <MetricCard
          title="Historical Selection Rate"
          value={formatPercent(company.historicalSelectionRate)}
          subtitle="Proportion of accepted candidates"
          icon={<Percent size={20} />}
          accentColor="#38bdf8"
        />
        <MetricCard
          title="Avg. Selected CGPA"
          value={formatDecimal(company.historicalAverageSelectedCgpa, 2)}
          subtitle="Benchmark for selected applicants"
          icon={<GraduationCap size={20} />}
          accentColor="#10b981"
        />
        <MetricCard
          title="Total Processed Applications"
          value={formatNumber(company.totalApplications)}
          subtitle="Historical candidate interactions"
          icon={<FileText size={20} />}
          accentColor="#a855f7"
        />
      </div>
    </div>
  );
};
