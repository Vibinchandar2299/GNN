import React, { useEffect, useState } from 'react';
import { TrendingUp, Calendar, AlertCircle } from 'lucide-react';
import { analyticsApi } from '../../api/analyticsApi';
import { HiringTrend } from '../../types/analytics';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { Card } from '../../components/common/Card';
import { MetricCard } from '../../components/common/MetricCard';
import { formatNumber, formatPercent } from '../../utils/formatting';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  CartesianGrid,
  BarChart,
  Bar,
} from 'recharts';

export const HiringTrendsPage: React.FC = () => {
  const [trends, setTrends] = useState<HiringTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTrends = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await analyticsApi.getTrends();
      setTrends(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch recruitment trends.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrends();
  }, []);

  if (loading) {
    return <LoadingState message="Analyzing temporal recruitment cycles..." />;
  }

  if (error || trends.length === 0) {
    return (
      <ErrorState
        title="Trends Analytics Error"
        message={error || 'No trend records available from database.'}
        onRetry={fetchTrends}
      />
    );
  }

  // Format data for Recharts
  const chartData = trends.map((t) => ({
    cycle: `Cycle ${t.cycle}`,
    'Total Applications': t.totalApplications,
    'Selected Candidates': t.selectedCount,
    'Rejected Candidates': t.rejectedCount,
    'Selection Rate (%)': Number((t.selectionRate * 100).toFixed(1)),
  }));

  const totalAllApps = trends.reduce((sum, t) => sum + t.totalApplications, 0);
  const totalAllSelected = trends.reduce((sum, t) => sum + t.selectedCount, 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Historical Data Clarification Notice */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: '12px',
          padding: '14px 18px',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'rgba(16, 185, 129, 0.08)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: '#d1fae5',
          fontSize: '0.84rem',
          lineHeight: 1.5,
        }}
      >
        <AlertCircle size={18} style={{ color: 'var(--color-selected)', flexShrink: 0, marginTop: '2px' }} />
        <div>
          <strong style={{ color: 'var(--color-selected)', marginRight: '6px' }}>Temporal Dataset Label:</strong>
          These charts visualize <strong>Historical Hiring Data</strong> across observed academic recruitment cycles (2023–2026).
          They represent verified empirical outcomes and must not be interpreted as future predictive forecasts.
        </div>
      </div>

      {/* Cycle Summary Metrics */}
      <div className="grid-cols-4">
        <MetricCard
          title="Observed Cycles"
          value={trends.length}
          subtitle="2023 to 2026 academic drives"
          icon={<Calendar size={20} />}
          accentColor="#38bdf8"
        />
        <MetricCard
          title="Aggregated Applications"
          value={formatNumber(totalAllApps)}
          subtitle="Total candidate drives"
          icon={<TrendingUp size={20} />}
          accentColor="#10b981"
        />
        <MetricCard
          title="Historical Selections"
          value={formatNumber(totalAllSelected)}
          subtitle="Confirmed offers issued"
          icon={<TrendingUp size={20} />}
          accentColor="#f59e0b"
        />
        <MetricCard
          title="Overall Success Rate"
          value={formatPercent(totalAllApps > 0 ? totalAllSelected / totalAllApps : 0)}
          subtitle="Multi-cycle average"
          icon={<TrendingUp size={20} />}
          accentColor="#a855f7"
        />
      </div>

      {/* Temporal Line Chart: Selection Rate Progression */}
      <Card
        title="Selection Rate Temporal Progression"
        subtitle="Empirical selection probability percentage across consecutive recruitment drives"
      >
        <div style={{ width: '100%', height: '320px', marginTop: '12px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="cycle" stroke="#94a3b8" fontSize={12} />
              <YAxis stroke="#94a3b8" fontSize={12} domain={[40, 70]} unit="%" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#111827',
                  border: '1px solid #1e293b',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '0.85rem', paddingTop: '10px' }} />
              <Line
                type="monotone"
                dataKey="Selection Rate (%)"
                stroke="#38bdf8"
                strokeWidth={3}
                dot={{ r: 6, fill: '#38bdf8' }}
                activeDot={{ r: 8 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Volume Bar Chart: Applications per Cycle */}
      <Card
        title="Application Volume & Outcome Composition"
        subtitle="Selected vs Rejected volume decomposed by recruitment drive"
      >
        <div style={{ width: '100%', height: '320px', marginTop: '12px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
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
              <Bar dataKey="Selected Candidates" fill="#10b981" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Rejected Candidates" fill="#f43f5e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Cycle Numerical Breakdown Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Cycle Breakdown Data Table</h3>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.86rem' }}>
            <thead>
              <tr style={{ backgroundColor: 'var(--bg-elevated)', borderBottom: '1px solid var(--border-subtle)' }}>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Recruitment Cycle</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Total Applications</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Selected Count</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Rejected Count</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Selection Rate</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Research Split Role</th>
              </tr>
            </thead>
            <tbody>
              {trends.map((t) => {
                const role =
                  t.cycle === 2023 || t.cycle === 2024
                    ? 'Training Set'
                    : t.cycle === 2025
                    ? 'Validation Set'
                    : 'Test Set (Out-of-Distribution)';
                return (
                  <tr
                    key={t.cycle}
                    style={{
                      borderBottom: '1px solid var(--border-subtle)',
                      transition: 'background-color 0.15s ease',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--bg-card-hover)')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    <td style={{ padding: '14px 16px', fontWeight: 700, color: 'var(--text-primary)' }}>
                      Cycle {t.cycle}
                    </td>
                    <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)' }}>
                      {formatNumber(t.totalApplications)}
                    </td>
                    <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', color: 'var(--color-selected)', fontWeight: 600 }}>
                      {formatNumber(t.selectedCount)}
                    </td>
                    <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', color: 'var(--color-rejected)', fontWeight: 600 }}>
                      {formatNumber(t.rejectedCount)}
                    </td>
                    <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', color: 'var(--color-primary)', fontWeight: 600 }}>
                      {formatPercent(t.selectionRate)}
                    </td>
                    <td style={{ padding: '14px 16px', color: 'var(--text-muted)' }}>
                      <span
                        style={{
                          padding: '3px 8px',
                          borderRadius: '4px',
                          backgroundColor: 'var(--bg-elevated)',
                          fontSize: '0.75rem',
                        }}
                      >
                        {role}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
