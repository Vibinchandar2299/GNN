import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Play,
  Network,
  RotateCcw,
  Sparkles,
  Layers,
  GraduationCap,
  Clock,
  TrendingUp,
} from 'lucide-react';
import { applicationApi } from '../../api/applicationApi';
import { Application } from '../../types/application';
import { PredictionResponse } from '../../types/prediction';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { Card } from '../../components/common/Card';
import { MetricCard } from '../../components/common/MetricCard';
import { StatusBadge } from '../../components/common/StatusBadge';
import { ProbabilityBar } from '../../components/common/ProbabilityBar';
import { DisclaimerCard } from '../../components/common/DisclaimerCard';
import { formatPercent, formatDecimal } from '../../utils/formatting';
import { DECISION_SUPPORT_LABEL } from '../../utils/constants';

export const ApplicationDetailPage: React.FC = () => {
  const { applicationId } = useParams<{ applicationId: string }>();
  const navigate = useNavigate();

  const [application, setApplication] = useState<Application | null>(null);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [predictionError, setPredictionError] = useState<string | null>(null);

  const fetchApplication = async () => {
    if (!applicationId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await applicationApi.getApplicationById(applicationId);
      setApplication(data);
      if (data.latestPrediction) {
        setPrediction(data.latestPrediction);
      }
    } catch (err: any) {
      setError(err.message || `Failed to fetch application ${applicationId}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplication();
  }, [applicationId]);

  const handleRunPrediction = async (forceRefresh: boolean = false) => {
    if (!applicationId) return;
    setPredicting(true);
    setPredictionError(null);
    try {
      const result = await applicationApi.predictApplication(applicationId, {
        modelName: 'AMRG-GraphSAGE',
        modelVersion: 'research-v1',
        forceRefresh,
      });
      setPrediction(result);
    } catch (err: any) {
      setPredictionError(
        err.message || 'Failed to obtain model-estimated outcome from FastAPI inference service.'
      );
    } finally {
      setPredicting(false);
    }
  };

  if (loading) {
    return <LoadingState message={`Retrieving application records for ${applicationId}...`} />;
  }

  if (error || !application) {
    return (
      <ErrorState
        title="Application Record Not Found"
        message={error || `Could not find application ${applicationId}`}
        onRetry={fetchApplication}
      />
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Navigation & Action Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button
          onClick={() => navigate('/applications')}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            color: 'var(--text-secondary)',
            fontSize: '0.88rem',
            cursor: 'pointer',
          }}
        >
          <ArrowLeft size={16} /> Back to Applications
        </button>

        <button
          onClick={() => navigate(`/graph?type=application&id=${application.applicationId}`)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'rgba(56, 189, 248, 0.15)',
            border: '1px solid rgba(56, 189, 248, 0.4)',
            color: 'var(--color-primary)',
            fontSize: '0.85rem',
            fontWeight: 600,
          }}
        >
          <Network size={16} /> Explore Application Knowledge Subgraph
        </button>
      </div>

      {/* Mandatory Decision-Support Disclaimer Card */}
      <DisclaimerCard />

      {/* SECTION 1 — APPLICATION CONTEXT */}
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
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
              {application.applicationId}
            </h2>
            <span
              style={{
                padding: '3px 10px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--bg-elevated)',
                fontSize: '0.8rem',
                color: 'var(--text-secondary)',
              }}
            >
              Recruitment Cycle {application.cycle}
            </span>
          </div>
          <div style={{ display: 'flex', gap: '16px', marginTop: '8px', fontSize: '0.85rem' }}>
            <span>
              Candidate:{' '}
              <button
                onClick={() => navigate(`/candidates/${application.studentId}`)}
                style={{ color: 'var(--color-primary)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}
              >
                {application.studentId}
              </button>
            </span>
            <span>•</span>
            <span>
              Company:{' '}
              <button
                onClick={() => navigate(`/companies/${application.companyId}`)}
                style={{ color: '#f59e0b', fontFamily: 'var(--font-mono)', fontWeight: 600 }}
              >
                {application.companyId}
              </button>
            </span>
            <span>•</span>
            <span>
              Job Spec:{' '}
              <button
                onClick={() => navigate(`/jobs/${application.jobId}`)}
                style={{ color: '#a855f7', fontFamily: 'var(--font-mono)', fontWeight: 600 }}
              >
                {application.jobId}
              </button>
            </span>
          </div>
        </div>

        {/* Historical Outcome Badge */}
        <div style={{ textAlign: 'right' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
            Historical Ground Truth
          </span>
          <StatusBadge status={application.finalStatus} />
        </div>
      </div>

      {/* SECTION 2 — MODEL ESTIMATE (PREDICTION CARD) */}
      <Card
        title={DECISION_SUPPORT_LABEL}
        subtitle="Forward-pass inference via Adaptive Multi-Relational GraphSAGE (AMRG-GraphSAGE)"
        action={
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => handleRunPrediction(false)}
              disabled={predicting}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '9px 18px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--color-primary-dark)',
                color: '#ffffff',
                fontSize: '0.86rem',
                fontWeight: 600,
                opacity: predicting ? 0.7 : 1,
                cursor: predicting ? 'not-allowed' : 'pointer',
                boxShadow: '0 0 12px rgba(56, 189, 248, 0.3)',
              }}
            >
              {predicting ? <RotateCcw size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Play size={16} />}
              {prediction ? 'Re-evaluate Prediction' : 'Run Model Prediction'}
            </button>
          </div>
        }
      >
        {predicting ? (
          <LoadingState message="Executing AMRG-GraphSAGE inference on multi-relational graph..." minHeight="160px" />
        ) : predictionError ? (
          <div style={{ padding: '16px', color: 'var(--color-rejected)', fontSize: '0.86rem' }}>
            <strong>Prediction Error:</strong> {predictionError}
          </div>
        ) : prediction ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginTop: '10px' }}>
            {/* Side by side comparison: Ground Truth vs Model Estimate */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '20px',
                padding: '18px',
                backgroundColor: 'var(--bg-elevated)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Historical Ground Truth Outcome</span>
                <div style={{ marginTop: '6px' }}>
                  <StatusBadge status={application.finalStatus} />
                </div>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                  Recorded during Cycle {application.cycle} corporate recruitment drive.
                </p>
              </div>

              <div>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Model-Estimated Outcome</span>
                <div style={{ marginTop: '6px' }}>
                  <StatusBadge status={prediction.predictedStatus} isModelEstimate />
                </div>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                  Computed by {prediction.modelName} ({prediction.modelVersion})
                </p>
              </div>
            </div>

            {/* Estimated Probability Bar */}
            <div style={{ padding: '0 4px' }}>
              <ProbabilityBar probability={prediction.estimatedProbability} />
            </div>

            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              {prediction.disclaimer}
            </div>
          </div>
        ) : (
          <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.88rem' }}>
            No model prediction currently calculated for this application. Click{' '}
            <strong style={{ color: 'var(--color-primary)' }}>"Run Model Prediction"</strong> to execute live
            AMRG-GraphSAGE forward pass.
          </div>
        )}
      </Card>

      {/* SECTION 3 — OBSERVABLE DECISION-SUPPORT ATTRIBUTES */}
      <section>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '14px', color: 'var(--text-secondary)' }}>
          Observable Decision-Support Attributes
        </h3>
        <div className="grid-cols-4">
          <MetricCard
            title="Relevant Experience"
            value={`${application.relevantExperienceMonths} Months`}
            subtitle="Prior technical exposure"
            icon={<Clock size={18} />}
            accentColor="#38bdf8"
          />
          <MetricCard
            title="Skill Match Ratio"
            value={formatPercent(application.skillMatchRatio)}
            subtitle="Mandated skill overlap"
            icon={<Layers size={18} />}
            accentColor="#10b981"
          />
          <MetricCard
            title="Total Skill Count"
            value={application.totalSkillCount}
            subtitle={`Avg proficiency: ${formatDecimal(application.averageSkillProficiency, 2)}`}
            icon={<Sparkles size={18} />}
            accentColor="#f59e0b"
          />
          <MetricCard
            title="Role Experience Match"
            value={formatPercent(application.roleExperienceMatch)}
            subtitle={`Role shift: ${formatDecimal(application.roleShiftScore, 2)}`}
            icon={<TrendingUp size={18} />}
            accentColor="#a855f7"
          />
        </div>
      </section>

      {/* Additional Feature Details */}
      <div className="grid-cols-2">
        <Card title="Skill Level Alignment" subtitle="Quantitative competency gap assessment">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.86rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Required Skill Level Gap:</span>
              <strong style={{ fontFamily: 'var(--font-mono)', color: application.requiredSkillLevelGap > 0 ? 'var(--color-rejected)' : 'var(--color-selected)' }}>
                {formatDecimal(application.requiredSkillLevelGap, 2)}
              </strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Average Skill Proficiency:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>{formatDecimal(application.averageSkillProficiency, 2)}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Role Shift Score:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>{formatDecimal(application.roleShiftScore, 2)}</strong>
            </div>
          </div>
        </Card>

        <Card title="Hiring Quota Context" subtitle="Target company demand constraints">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.86rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Expected Hiring Count:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>{application.expectedHiringCount} vacancies</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Recruitment Cycle:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>Cycle {application.cycle}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Graph Representation:</span>
              <strong style={{ color: 'var(--color-primary)' }}>Node Type: Application</strong>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
