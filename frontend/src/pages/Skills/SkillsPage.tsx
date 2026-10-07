import React, { useEffect, useState } from 'react';
import { Layers, AlertCircle } from 'lucide-react';
import { skillApi } from '../../api/skillApi';
import { Skill, SkillDemand } from '../../types/skill';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { Card } from '../../components/common/Card';
import { MetricCard } from '../../components/common/MetricCard';
import { formatNumber, formatDecimal } from '../../utils/formatting';
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

export const SkillsPage: React.FC = () => {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [demandList, setDemandList] = useState<SkillDemand[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSkillsData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [skillsData, demandData] = await Promise.all([
        skillApi.getAllSkills(),
        skillApi.getSkillDemand(),
      ]);
      setSkills(skillsData);
      setDemandList(demandData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch skill taxonomy metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSkillsData();
  }, []);

  if (loading) {
    return <LoadingState message="Retrieving skill taxonomy and demand matrices..." />;
  }

  if (error) {
    return (
      <ErrorState
        title="Skill Taxonomy Error"
        message={error}
        onRetry={fetchSkillsData}
      />
    );
  }

  // Sort demand for chart visualization
  const sortedDemand = [...demandList]
    .sort((a, b) => b.demandCount - a.demandCount)
    .slice(0, 10)
    .map((s) => ({
      name: s.skillName,
      'Job Demand': s.demandCount,
      'Student Supply': s.supplyCount,
    }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Terminology Clarity Notice */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: '12px',
          padding: '14px 18px',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'rgba(56, 189, 248, 0.08)',
          border: '1px solid rgba(56, 189, 248, 0.3)',
          color: '#e0f2fe',
          fontSize: '0.84rem',
          lineHeight: 1.5,
        }}
      >
        <AlertCircle size={18} style={{ color: 'var(--color-primary)', flexShrink: 0, marginTop: '2px' }} />
        <div>
          <strong style={{ color: 'var(--color-primary)', marginRight: '6px' }}>Research Methodology Note:</strong>
          Market skill frequency and demand metrics represent observational distributions across job postings and student profiles.
          They must not be conflated with AMRG-GraphSAGE model feature importance or attribution weights.
        </div>
      </div>

      {/* Top Level Metric Cards */}
      <div className="grid-cols-3">
        <MetricCard
          title="Skill Ontology Size"
          value={skills.length}
          subtitle="Fixed ontology entities"
          icon={<Layers size={20} />}
          accentColor="#38bdf8"
        />
        <MetricCard
          title="Highest Demand Skill"
          value={demandList[0]?.skillName || 'Python'}
          subtitle={`${demandList[0]?.demandCount || 0} job openings`}
          icon={<Layers size={20} />}
          accentColor="#10b981"
        />
        <MetricCard
          title="Total Student Proficiencies"
          value={formatNumber(skills.reduce((acc, s) => acc + s.studentCount, 0))}
          subtitle="Skill acquisitions logged"
          icon={<Layers size={20} />}
          accentColor="#f59e0b"
        />
      </div>

      {/* Horizontal / Grouped Demand Bar Chart */}
      <Card
        title="Top 10 Demanded Skills vs. Student Supply"
        subtitle="Market requirements compared against candidate skill proficiencies"
      >
        <div style={{ width: '100%', height: '380px', marginTop: '12px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={sortedDemand}
              layout="vertical"
              margin={{ top: 10, right: 30, left: 40, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
              <XAxis type="number" stroke="#94a3b8" fontSize={12} />
              <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={12} width={110} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#111827',
                  border: '1px solid #1e293b',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '0.85rem', paddingTop: '10px' }} />
              <Bar dataKey="Job Demand" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
              <Bar dataKey="Student Supply" fill="#38bdf8" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Complete Skill Taxonomy Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>All 18 Research Skill Entities</h3>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.86rem' }}>
            <thead>
              <tr style={{ backgroundColor: 'var(--bg-elevated)', borderBottom: '1px solid var(--border-subtle)' }}>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Skill ID</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Skill Name</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Job Demand (Count)</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Student Supply (Count)</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Demand / Supply Ratio</th>
              </tr>
            </thead>
            <tbody>
              {demandList.map((s) => (
                <tr
                  key={s.skillId}
                  style={{
                    borderBottom: '1px solid var(--border-subtle)',
                    transition: 'background-color 0.15s ease',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--bg-card-hover)')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                >
                  <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#f43f5e' }}>
                    {s.skillId}
                  </td>
                  <td style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {s.skillName}
                  </td>
                  <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', color: '#a855f7', fontWeight: 600 }}>
                    {formatNumber(s.demandCount)}
                  </td>
                  <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', color: 'var(--color-primary)' }}>
                    {formatNumber(s.supplyCount)}
                  </td>
                  <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                    {formatDecimal(s.demandRatio, 3)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
