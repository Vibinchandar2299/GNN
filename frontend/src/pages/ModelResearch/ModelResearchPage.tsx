import React, { useEffect, useState } from 'react';
import {
  BrainCircuit,
  Award,
  Layers,
  Cpu,
  ShieldAlert,
  CheckCircle2,
  Calendar,
  Network,
} from 'lucide-react';
import { modelApi } from '../../api/modelApi';
import { ModelBenchmark, ModelMetadata } from '../../types/model';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { Card } from '../../components/common/Card';
import { MetricCard } from '../../components/common/MetricCard';
import { formatDecimal } from '../../utils/formatting';
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

export const ModelResearchPage: React.FC = () => {
  const [benchmarks, setBenchmarks] = useState<ModelBenchmark[]>([]);
  const [metadata, setMetadata] = useState<ModelMetadata | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchModelData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [bData, mData] = await Promise.all([
        modelApi.getBenchmarks(),
        modelApi.getMetadata(),
      ]);
      setBenchmarks(bData);
      setMetadata(mData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch model research specifications.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModelData();
  }, []);

  if (loading) {
    return <LoadingState message="Retrieving AMRG-GraphSAGE research artifacts and benchmark metrics..." />;
  }

  if (error || benchmarks.length === 0) {
    return (
      <ErrorState
        title="Model Benchmark Data Error"
        message={error || 'Unable to load benchmark data.'}
        onRetry={fetchModelData}
      />
    );
  }

  // Find standard vs AMRG
  const standard = benchmarks.find((b) => b.modelName.includes('Standard') || b.modelName.includes('Baseline'));
  const amrg = benchmarks.find((b) => b.modelName.includes('AMRG'));

  // Prepare chart comparison data
  const metricChartData = [
    {
      metric: 'Accuracy',
      'Standard GraphSAGE': standard ? Number((standard.accuracy * 100).toFixed(2)) : 83.87,
      'AMRG-GraphSAGE (Proposed)': amrg ? Number((amrg.accuracy * 100).toFixed(2)) : 84.27,
    },
    {
      metric: 'Precision',
      'Standard GraphSAGE': standard ? Number((standard.precisionScore * 100).toFixed(2)) : 84.43,
      'AMRG-GraphSAGE (Proposed)': amrg ? Number((amrg.precisionScore * 100).toFixed(2)) : 84.93,
    },
    {
      metric: 'Recall',
      'Standard GraphSAGE': standard ? Number((standard.recall * 100).toFixed(2)) : 86.99,
      'AMRG-GraphSAGE (Proposed)': amrg ? Number((amrg.recall * 100).toFixed(2)) : 87.14,
    },
    {
      metric: 'F1 Score',
      'Standard GraphSAGE': standard ? Number((standard.f1Score * 100).toFixed(2)) : 85.69,
      'AMRG-GraphSAGE (Proposed)': amrg ? Number((amrg.f1Score * 100).toFixed(2)) : 86.02,
    },
    {
      metric: 'ROC-AUC',
      'Standard GraphSAGE': standard ? Number((standard.rocAuc * 100).toFixed(2)) : 91.40,
      'AMRG-GraphSAGE (Proposed)': amrg ? Number((amrg.rocAuc * 100).toFixed(2)) : 91.42,
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Paper Header Card */}
      <div
        className="card"
        style={{
          borderLeft: '4px solid var(--color-primary)',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span
            style={{
              padding: '3px 10px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'rgba(56, 189, 248, 0.15)',
              fontSize: '0.76rem',
              color: 'var(--color-primary)',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            Research Benchmark
          </span>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Model Artifact: AMRG_GraphSAGE_model.pt
          </span>
        </div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
          {metadata?.researchTitle ||
            'An Explainable AMRG-GraphSAGE Framework for Hiring Pattern Analysis under Evolving Job Requirements'}
        </h2>
        <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          Evaluating adaptive multi-relational neighborhood aggregation against baseline GraphSAGE across temporal placement cycles.
        </p>
      </div>

      {/* Primary Research Metrics */}
      {amrg && (
        <div className="grid-cols-4">
          <MetricCard
            title="Accuracy"
            value={formatDecimal(amrg.accuracy, 4)}
            subtitle="+0.40% over baseline GraphSAGE"
            icon={<Award size={20} />}
            accentColor="#10b981"
          />
          <MetricCard
            title="ROC-AUC"
            value={formatDecimal(amrg.rocAuc, 4)}
            subtitle="Area under ROC curve"
            icon={<BrainCircuit size={20} />}
            accentColor="#38bdf8"
          />
          <MetricCard
            title="F1 Score"
            value={formatDecimal(amrg.f1Score, 4)}
            subtitle="Harmonic mean precision-recall"
            icon={<Award size={20} />}
            accentColor="#a855f7"
          />
          <MetricCard
            title="Recall"
            value={formatDecimal(amrg.recall, 4)}
            subtitle="Sensitivity across test set"
            icon={<Award size={20} />}
            accentColor="#f59e0b"
          />
        </div>
      )}

      {/* Head-to-Head Benchmark Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Empirical Benchmark Comparison</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>
            Direct comparison between baseline uniform aggregation and adaptive multi-relational aggregation
          </p>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.86rem' }}>
            <thead>
              <tr style={{ backgroundColor: 'var(--bg-elevated)', borderBottom: '1px solid var(--border-subtle)' }}>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Model Name</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Accuracy</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Precision</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Recall</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>F1-Score</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>ROC-AUC</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Description</th>
              </tr>
            </thead>
            <tbody>
              {benchmarks.map((b) => {
                const isAmrg = b.modelName.includes('AMRG');
                return (
                  <tr
                    key={b.modelName}
                    style={{
                      borderBottom: '1px solid var(--border-subtle)',
                      backgroundColor: isAmrg ? 'rgba(56, 189, 248, 0.04)' : 'transparent',
                    }}
                  >
                    <td style={{ padding: '14px 16px', fontWeight: 700, color: isAmrg ? 'var(--color-primary)' : 'var(--text-primary)' }}>
                      {b.modelName} {isAmrg && '(Proposed)'}
                    </td>
                    <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', fontWeight: isAmrg ? 700 : 400 }}>
                      {formatDecimal(b.accuracy, 4)}
                    </td>
                    <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', fontWeight: isAmrg ? 700 : 400 }}>
                      {formatDecimal(b.precisionScore, 4)}
                    </td>
                    <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', fontWeight: isAmrg ? 700 : 400 }}>
                      {formatDecimal(b.recall, 4)}
                    </td>
                    <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', fontWeight: isAmrg ? 700 : 400 }}>
                      {formatDecimal(b.f1Score, 4)}
                    </td>
                    <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', fontWeight: isAmrg ? 700 : 400, color: 'var(--color-selected)' }}>
                      {formatDecimal(b.rocAuc, 4)}
                    </td>
                    <td style={{ padding: '14px 16px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      {b.datasetDescription}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Comparative Performance Chart */}
      <Card
        title="Comparative Evaluation Metrics (%)"
        subtitle="Side-by-side metric comparison on the out-of-distribution Test Set (Cycle 2026)"
      >
        <div style={{ width: '100%', height: '320px', marginTop: '12px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={metricChartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis dataKey="metric" stroke="#94a3b8" fontSize={12} />
              <YAxis stroke="#94a3b8" fontSize={12} domain={[80, 95]} unit="%" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#111827',
                  border: '1px solid #1e293b',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '0.85rem', paddingTop: '10px' }} />
              <Bar dataKey="Standard GraphSAGE" fill="#64748b" radius={[4, 4, 0, 0]} />
              <Bar dataKey="AMRG-GraphSAGE (Proposed)" fill="#38bdf8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Architecture & Evaluation Protocol Grid */}
      <div className="grid-cols-2">
        {/* Architecture Specs */}
        <Card title="GNN Architecture Specifications" subtitle="Deep network topology of AMRG-GraphSAGE">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.85rem', marginTop: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Graph Layers:</span>
              <strong>2 Multi-Relational Convolutional Layers</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Hidden Representation:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>128 Channels</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Relation Embedding Dimension:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>16 Channels</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Convolution Core:</span>
              <strong style={{ color: 'var(--color-primary)' }}>RelationAwareWeightedSAGEConv</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Adaptive Mechanisms:</span>
              <strong>Relation-Scoring • Confidence Gating • Multi-Scale Fusion</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Regularization:</span>
              <strong>LayerNorm • ReLU • Dropout (0.20)</strong>
            </div>
          </div>
        </Card>

        {/* Temporal Evaluation Protocol */}
        <Card title="Temporal Evaluation Protocol" subtitle="Strict out-of-distribution temporal splitting">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.85rem', marginTop: '6px' }}>
            <div style={{ padding: '12px', backgroundColor: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600 }}>
                <span style={{ color: 'var(--color-primary)' }}>Training Phase (Cycles 2023–2024)</span>
                <span style={{ fontFamily: 'var(--font-mono)' }}>1,594 Applications</span>
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                614 applications in Cycle 2023 + 980 applications in Cycle 2024.
              </p>
            </div>

            <div style={{ padding: '12px', backgroundColor: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600 }}>
                <span style={{ color: '#f59e0b' }}>Validation Phase (Cycle 2025)</span>
                <span style={{ fontFamily: 'var(--font-mono)' }}>1,160 Applications</span>
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                Used strictly for hyperparameter selection and early stopping.
              </p>
            </div>

            <div style={{ padding: '12px', backgroundColor: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600 }}>
                <span style={{ color: 'var(--color-selected)' }}>Evaluation Test Phase (Cycle 2026)</span>
                <span style={{ fontFamily: 'var(--font-mono)' }}>1,246 Applications</span>
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                Final out-of-distribution evaluation under evolving job market requirements.
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* EXPLAINABILITY HANDLING (SECTION 22) */}
      <div
        className="card"
        style={{
          borderLeft: '4px solid #f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.04)',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <ShieldAlert size={20} style={{ color: '#f59e0b' }} />
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#f59e0b' }}>
            Explainability Module Status: Experimental / Currently Unavailable
          </h3>
        </div>
        <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          {metadata?.explainability?.status_note ||
            'GNNExplainer encountered PyTorch Geometric edge-gradient compatibility limitations with custom RelationAwareWeightedSAGEConv. In accordance with strict scientific integrity principles, no synthetic feature importance or fabricated attribution explanations are generated.'}
        </p>
        <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          To inspect candidate-job compatibility, use the observable attributes and multi-relational graph neighborhood
          explorer instead.
        </div>
      </div>
    </div>
  );
};
