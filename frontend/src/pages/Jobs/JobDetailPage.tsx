import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Briefcase,
  GraduationCap,
  Clock,
  Layers,
  Network,
  CheckCircle2,
} from 'lucide-react';
import { jobApi } from '../../api/jobApi';
import { Job } from '../../types/job';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { MetricCard } from '../../components/common/MetricCard';
import { Card } from '../../components/common/Card';
import { DisclaimerCard } from '../../components/common/DisclaimerCard';
import { formatCurrencyLpa, formatDecimal } from '../../utils/formatting';

export const JobDetailPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchJob = async () => {
    if (!jobId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await jobApi.getJobById(jobId);
      setJob(data);
    } catch (err: any) {
      setError(err.message || `Failed to fetch job specification for ${jobId}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJob();
  }, [jobId]);

  if (loading) {
    return <LoadingState message={`Retrieving job specification for ${jobId}...`} />;
  }

  if (error || !job) {
    return (
      <ErrorState
        title="Job Specification Not Found"
        message={error || `Could not find job with ID ${jobId}`}
        onRetry={fetchJob}
      />
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button
          onClick={() => navigate('/jobs')}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            color: 'var(--text-secondary)',
            fontSize: '0.88rem',
            cursor: 'pointer',
          }}
        >
          <ArrowLeft size={16} /> Back to Job Postings Catalog
        </button>

        <button
          onClick={() => navigate(`/graph?type=job&id=${job.jobId}`)}
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
          <Network size={16} /> Explore Job Knowledge Subgraph
        </button>
      </div>

      <DisclaimerCard customText="Job criteria and competency requirements are benchmarked against historical corporate placement drives in the research corpus." />

      {/* Job Header */}
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
              backgroundColor: 'rgba(168, 85, 247, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#a855f7',
              border: '1px solid rgba(168, 85, 247, 0.4)',
            }}
          >
            <Briefcase size={28} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>
                {job.jobTitle}
              </h2>
              <span
                style={{
                  padding: '2px 8px',
                  borderRadius: '4px',
                  backgroundColor: 'var(--bg-elevated)',
                  fontSize: '0.78rem',
                  fontFamily: 'var(--font-mono)',
                  color: '#a855f7',
                }}
              >
                {job.jobId}
              </span>
            </div>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Functional Domain: <strong style={{ color: 'var(--text-secondary)' }}>{job.jobDomain}</strong>
            </p>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Annual Package</span>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--color-selected)', fontFamily: 'var(--font-mono)' }}>
            {formatCurrencyLpa(job.salaryLpa)}
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid-cols-3">
        <MetricCard
          title="Minimum CGPA Cutoff"
          value={formatDecimal(job.minimumCgpa, 2)}
          subtitle="Eligibility prerequisite"
          icon={<GraduationCap size={20} />}
          accentColor="#38bdf8"
        />
        <MetricCard
          title="Required Experience"
          value={`${job.experienceRequiredMonths} Months`}
          subtitle="Internship or project background"
          icon={<Clock size={20} />}
          accentColor="#10b981"
        />
        <MetricCard
          title="Required Skill Count"
          value={job.requiredSkillCount}
          subtitle="Mandatory competencies"
          icon={<Layers size={20} />}
          accentColor="#f59e0b"
        />
      </div>

      {/* Required Skills Section */}
      <Card title="Required Competencies" subtitle="Specific skills mandated by this job profile">
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px' }}>
          {job.requiredSkills && job.requiredSkills.length > 0 ? (
            job.requiredSkills.map((skill) => (
              <span
                key={skill}
                style={{
                  padding: '6px 14px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'rgba(168, 85, 247, 0.1)',
                  color: '#c084fc',
                  border: '1px solid rgba(168, 85, 247, 0.3)',
                  fontSize: '0.86rem',
                  fontWeight: 500,
                }}
              >
                {skill}
              </span>
            ))
          ) : (
            <span style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>No specific skills specified.</span>
          )}
        </div>
      </Card>

      {/* Observable Candidate Profile vs Job Requirement comparison note */}
      <Card
        title="Observable Requirement Matching Protocol"
        subtitle="Analytical comparison framework (Not GNNExplainer feature attribution)"
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
            <CheckCircle2 size={16} style={{ color: 'var(--color-primary)', marginTop: '3px', flexShrink: 0 }} />
            <span>
              <strong>Academic Threshold:</strong> Applicants must satisfy the minimum CGPA cutoff ({formatDecimal(job.minimumCgpa, 2)}) to qualify for preliminary corporate shortlisting.
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
            <CheckCircle2 size={16} style={{ color: 'var(--color-primary)', marginTop: '3px', flexShrink: 0 }} />
            <span>
              <strong>Skill Coverage Ratio:</strong> Calculated as the proportion of the job's {job.requiredSkillCount} mandated skills present in the applicant's skill repository.
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
            <CheckCircle2 size={16} style={{ color: 'var(--color-primary)', marginTop: '3px', flexShrink: 0 }} />
            <span>
              <strong>Experience Alignment:</strong> Evaluation of prior practical engineering exposure against the target benchmark of {job.experienceRequiredMonths} months.
            </span>
          </div>
        </div>
      </Card>
    </div>
  );
};
