import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  GraduationCap,
  Code,
  Award,
  Layers,
  Network,
  BookOpen,
} from 'lucide-react';
import { candidateApi } from '../../api/candidateApi';
import { Candidate } from '../../types/candidate';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { Card } from '../../components/common/Card';
import { MetricCard } from '../../components/common/MetricCard';
import { DisclaimerCard } from '../../components/common/DisclaimerCard';
import { formatDecimal } from '../../utils/formatting';

export const CandidateDetailPage: React.FC = () => {
  const { studentId } = useParams<{ studentId: string }>();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCandidate = async () => {
    if (!studentId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await candidateApi.getCandidateById(studentId);
      setCandidate(data);
    } catch (err: any) {
      setError(err.message || `Failed to fetch candidate profile for ${studentId}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidate();
  }, [studentId]);

  if (loading) {
    return <LoadingState message={`Retrieving student profile for ${studentId}...`} />;
  }

  if (error || !candidate) {
    return (
      <ErrorState
        title="Student Record Not Found"
        message={error || `Could not find candidate with ID ${studentId}`}
        onRetry={fetchCandidate}
      />
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Back button and page title */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button
          onClick={() => navigate('/candidates')}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            color: 'var(--text-secondary)',
            fontSize: '0.88rem',
            cursor: 'pointer',
          }}
        >
          <ArrowLeft size={16} /> Back to Candidates Roster
        </button>

        <button
          onClick={() => navigate(`/graph?type=student&id=${candidate.studentId}`)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'rgba(168, 85, 247, 0.15)',
            border: '1px solid rgba(168, 85, 247, 0.4)',
            color: '#c084fc',
            fontSize: '0.85rem',
            fontWeight: 600,
          }}
        >
          <Network size={16} /> Explore Student Knowledge Subgraph
        </button>
      </div>

      {/* Decision-support note */}
      <DisclaimerCard customText="Candidate attributes shown below represent historical academic and competency records in the research database." />

      {/* Profile Header */}
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
              backgroundColor: 'rgba(16, 185, 129, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--color-selected)',
              border: '1px solid rgba(16, 185, 129, 0.4)',
            }}
          >
            <GraduationCap size={28} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                {candidate.studentId}
              </h2>
              <span
                style={{
                  padding: '2px 8px',
                  borderRadius: '4px',
                  backgroundColor: 'var(--bg-elevated)',
                  fontSize: '0.78rem',
                  color: 'var(--text-secondary)',
                }}
              >
                {candidate.department}
              </span>
            </div>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Resume Quality Score: <strong>{formatDecimal(candidate.resumeScore, 1)}</strong> / 100
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '20px' }}>
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Cumulative GPA</span>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--color-primary)', fontFamily: 'var(--font-mono)' }}>
              {formatDecimal(candidate.cgpa, 2)}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Active Backlogs</span>
            <div
              style={{
                fontSize: '1.6rem',
                fontWeight: 800,
                color: candidate.backlogs === 0 ? 'var(--color-selected)' : 'var(--color-rejected)',
                fontFamily: 'var(--font-mono)',
              }}
            >
              {candidate.backlogs}
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid-cols-4">
        <MetricCard
          title="Coding Proficiency"
          value={formatDecimal(candidate.codingScorePre, 1)}
          subtitle="Pre-recruitment assessment"
          icon={<Code size={18} />}
          accentColor="#38bdf8"
        />
        <MetricCard
          title="Aptitude Score"
          value={formatDecimal(candidate.aptitudeScorePre, 1)}
          subtitle="Analytical & problem solving"
          icon={<BookOpen size={18} />}
          accentColor="#10b981"
        />
        <MetricCard
          title="Communication Score"
          value={formatDecimal(candidate.communicationScorePre, 1)}
          subtitle="Verbal & written assessment"
          icon={<Award size={18} />}
          accentColor="#f59e0b"
        />
        <MetricCard
          title="Verified Experience"
          value={`${candidate.projectsCount} Proj • ${candidate.internshipsCount} Intern`}
          subtitle={`${candidate.certificationsCount} Certifications completed`}
          icon={<Layers size={18} />}
          accentColor="#a855f7"
        />
      </div>

      {/* Acquired Skills */}
      <Card title="Acquired Skill Profile" subtitle="Competencies mapped to the AMRG-GraphSAGE skill ontology">
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px' }}>
          {candidate.skills && candidate.skills.length > 0 ? (
            candidate.skills.map((skill) => (
              <span
                key={skill}
                style={{
                  padding: '6px 14px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'rgba(56, 189, 248, 0.1)',
                  color: 'var(--color-primary)',
                  border: '1px solid rgba(56, 189, 248, 0.3)',
                  fontSize: '0.86rem',
                  fontWeight: 500,
                }}
              >
                {skill}
              </span>
            ))
          ) : (
            <span style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>No acquired skills recorded.</span>
          )}
        </div>
      </Card>
    </div>
  );
};
