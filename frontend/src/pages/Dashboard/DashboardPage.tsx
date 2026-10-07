import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Users,
  Building2,
  Briefcase,
  Layers,
  CheckCircle2,
  XCircle,
  Percent,
  TrendingUp,
  BrainCircuit,
  Network,
  ArrowRight,
} from 'lucide-react';
import { dashboardApi } from '../../api/dashboardApi';
import { analyticsApi } from '../../api/analyticsApi';
import { DashboardSummary } from '../../types/dashboard';
import { HiringTrend } from '../../types/analytics';
import { MetricCard } from '../../components/common/MetricCard';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { Card } from '../../components/common/Card';
import { DisclaimerCard } from '../../components/common/DisclaimerCard';
import { formatNumber, formatPercent } from '../../utils/formatting';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  CartesianGrid,
} from 'recharts';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [trends, setTrends] = useState<HiringTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumData, trendData] = await Promise.all([
        dashboardApi.getSummary(),
        analyticsApi.getTrends(),
      ]);
      setSummary(sumData);
      setTrends(trendData);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard metrics from backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return <LoadingState message="Connecting to Spring Boot backend and retrieving dashboard metrics..." />;
  }

  if (error || !summary) {
    return (
      <ErrorState
        title="Dashboard Unavailable"
        message={error || 'Unable to retrieve dashboard metrics.'}
        onRetry={fetchDashboardData}
      />
    );
  }

  // Prepare trend chart data
  const chartData = trends.map((t) => ({
    cycle: `Cycle ${t.cycle}`,
    Selected: t.selectedCount,
    Rejected: t.rejectedCount,
    Total: t.totalApplications,
    Rate: (t.selectionRate * 100).toFixed(1),
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Banner Notice */}
      <DisclaimerCard />

      {/* KPI Overview Cards */}
      <section>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '16px', color: 'var(--text-secondary)' }}>
          Research Dataset Scale
        </h2>
        <div className="grid-cols-4">
          <MetricCard
            title="Total Applications"
            value={formatNumber(summary.totalApplications)}
            subtitle="Full research dataset"
            icon={<FileText size={20} />}
            accentColor="#38bdf8"
          />
          <MetricCard
            title="Registered Students"
            value={formatNumber(summary.totalStudents)}
            subtitle="Unique student profiles"
            icon={<Users size={20} />}
            accentColor="#10b981"
          />
          <MetricCard
            title="Partner Companies"
            value={formatNumber(summary.totalCompanies)}
            subtitle="Corporate recruiters"
            icon={<Building2 size={20} />}
            accentColor="#f59e0b"
          />
          <MetricCard
            title="Job Profiles"
            value={formatNumber(summary.totalJobs)}
            subtitle="Job openings catalog"
            icon={<Briefcase size={20} />}
            accentColor="#a855f7"
          />
        </div>
      </section>

      {/* Outcome KPI Cards */}
      <section>
        <div className="grid-cols-4">
          <MetricCard
            title="Distinct Skills"
            value={formatNumber(summary.totalSkills)}
            subtitle="Skill ontology taxonomy"
            icon={<Layers size={20} />}
            accentColor="#f43f5e"
          />
          <MetricCard
            title="Selected Outcomes"
            value={formatNumber(summary.selectedCount)}
            subtitle="Historical ground truth"
            icon={<CheckCircle2 size={20} />}
            accentColor="var(--color-selected)"
          />
          <MetricCard
            title="Rejected Outcomes"
            value={formatNumber(summary.rejectedCount)}
            subtitle="Historical ground truth"
            icon={<XCircle size={20} />}
            accentColor="var(--color-rejected)"
          />
          <MetricCard
            title="Overall Selection Rate"
            value={formatPercent(summary.selectionRate)}
            subtitle="Aggregate baseline"
            icon={<Percent size={20} />}
            accentColor="#06b6d4"
          />
        </div>
      </section>

      {/* Visualizations Section */}
      <div className="grid-cols-2">
        {/* Recruitment Cycle Outcomes Chart */}
        <Card
          title="Recruitment Cycle Distribution"
          subtitle="Selected vs Rejected applications across academic cycles (2023–2026)"
        >
          <div style={{ width: '100%', height: '300px', marginTop: '12px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="cycle" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#111827',
                    border: '1px solid #1e293b',
                    borderRadius: '8px',
                    fontSize: '0.85rem',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '0.85rem', paddingTop: '10px' }} />
                <Bar dataKey="Selected" fill="#10b981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Rejected" fill="#f43f5e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Research Model Overview Card */}
        <Card
          title="AMRG-GraphSAGE Research Model"
          subtitle="Adaptive Multi-Relational GraphSAGE for evolving job requirements"
          action={
            <button
              onClick={() => navigate('/model')}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.82rem',
                color: 'var(--color-primary)',
                fontWeight: 600,
              }}
            >
              Benchmarks <ArrowRight size={14} />
            </button>
          }
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '8px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
              <div style={{ padding: '12px', backgroundColor: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Graph Nodes</span>
                <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--color-primary)', fontFamily: 'var(--font-mono)' }}>
                  5,977
                </div>
              </div>
              <div style={{ padding: '12px', backgroundColor: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Multi-Relational Edges</span>
                <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#a855f7', fontFamily: 'var(--font-mono)' }}>
                  43,044
                </div>
              </div>
              <div style={{ padding: '12px', backgroundColor: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Relation Types</span>
                <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#f59e0b', fontFamily: 'var(--font-mono)' }}>
                  12
                </div>
              </div>
              <div style={{ padding: '12px', backgroundColor: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Node Features</span>
                <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#10b981', fontFamily: 'var(--font-mono)' }}>
                  82
                </div>
              </div>
            </div>

            <div style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              The proposed <strong>AMRG-GraphSAGE</strong> model achieves <strong>0.8427 Accuracy</strong> and{' '}
              <strong>0.9142 ROC-AUC</strong>, outperforming standard baseline GraphSAGE by learning relation-specific
              aggregation weights and feature-confidence gating.
            </div>
          </div>
        </Card>
      </div>

      {/* Quick Action Navigation Grid */}
      <section>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '16px', color: 'var(--text-secondary)' }}>
          Research Modules
        </h2>
        <div className="grid-cols-4">
          <div
            onClick={() => navigate('/applications')}
            className="card"
            style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: '8px' }}
          >
            <div style={{ color: 'var(--color-primary)' }}><FileText size={24} /></div>
            <strong style={{ fontSize: '0.95rem' }}>Application Explorer</strong>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Inspect candidate applications and trigger live AMRG-GraphSAGE inference.
            </p>
          </div>

          <div
            onClick={() => navigate('/graph')}
            className="card"
            style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: '8px' }}
          >
            <div style={{ color: '#a855f7' }}><Network size={24} /></div>
            <strong style={{ fontSize: '0.95rem' }}>Knowledge Graph</strong>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Explore focused subgraphs across students, companies, jobs, and skills.
            </p>
          </div>

          <div
            onClick={() => navigate('/trends')}
            className="card"
            style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: '8px' }}
          >
            <div style={{ color: '#10b981' }}><TrendingUp size={24} /></div>
            <strong style={{ fontSize: '0.95rem' }}>Hiring Trends</strong>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Analyze temporal shifts across training, validation, and test cycles.
            </p>
          </div>

          <div
            onClick={() => navigate('/model')}
            className="card"
            style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: '8px' }}
          >
            <div style={{ color: '#f59e0b' }}><BrainCircuit size={24} /></div>
            <strong style={{ fontSize: '0.95rem' }}>Model Research</strong>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Examine verified benchmark metrics and architecture specifications.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
