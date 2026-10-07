import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Network, Search, Layers, Play, AlertCircle } from 'lucide-react';
import { graphApi } from '../../api/graphApi';
import { GraphOverview, SubgraphResponse } from '../../types/graph';
import { SubgraphVisualizer } from '../../components/graph/SubgraphVisualizer';
import { GraphLegend } from '../../components/graph/GraphLegend';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { Card } from '../../components/common/Card';
import { MetricCard } from '../../components/common/MetricCard';
import { formatNumber } from '../../utils/formatting';

export const KnowledgeGraphPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [overview, setOverview] = useState<GraphOverview | null>(null);
  const [subgraph, setSubgraph] = useState<SubgraphResponse | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [loadingSubgraph, setLoadingSubgraph] = useState(false);
  const [errorOverview, setErrorOverview] = useState<string | null>(null);
  const [errorSubgraph, setErrorSubgraph] = useState<string | null>(null);

  // Focus parameters
  const initialType = searchParams.get('type') || 'application';
  const initialId = searchParams.get('id') || 'A00001';

  const [selectedType, setSelectedType] = useState<string>(initialType);
  const [selectedId, setSelectedId] = useState<string>(initialId);

  // Fetch overview on mount
  useEffect(() => {
    const fetchOverview = async () => {
      setLoadingOverview(true);
      setErrorOverview(null);
      try {
        const data = await graphApi.getOverview();
        setOverview(data);
      } catch (err: any) {
        setErrorOverview(err.message || 'Failed to fetch graph overview.');
      } finally {
        setLoadingOverview(false);
      }
    };
    fetchOverview();
  }, []);

  // Fetch subgraph for initial or changed parameters
  const fetchSubgraph = async (type: string, id: string) => {
    if (!id.trim()) return;
    setLoadingSubgraph(true);
    setErrorSubgraph(null);
    try {
      const data = await graphApi.getSubgraph(type.toLowerCase(), id.trim(), 35);
      setSubgraph(data);
      setSearchParams({ type, id });
    } catch (err: any) {
      setErrorSubgraph(
        err.message || `Failed to retrieve graph neighborhood for ${type} node ${id}.`
      );
    } finally {
      setLoadingSubgraph(false);
    }
  };

  useEffect(() => {
    fetchSubgraph(selectedType, selectedId);
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchSubgraph(selectedType, selectedId);
  };

  const handleNavigateToNode = (type: string, id: string) => {
    const t = type.toLowerCase();
    if (t === 'application') navigate(`/applications/${id}`);
    else if (t === 'student') navigate(`/candidates/${id}`);
    else if (t === 'company') navigate(`/companies/${id}`);
    else if (t === 'job') navigate(`/jobs/${id}`);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Information Banner */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: '12px',
          padding: '14px 18px',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'rgba(168, 85, 247, 0.08)',
          border: '1px solid rgba(168, 85, 247, 0.3)',
          color: '#f3e8ff',
          fontSize: '0.84rem',
          lineHeight: 1.5,
        }}
      >
        <AlertCircle size={18} style={{ color: '#c084fc', flexShrink: 0, marginTop: '2px' }} />
        <div>
          <strong style={{ color: '#c084fc', marginRight: '6px' }}>Focused Subgraph Explorer:</strong>
          The global placement knowledge graph contains <strong>5,977 nodes</strong> and <strong>43,044 multi-relational edges</strong>.
          To ensure optimal rendering performance and visual interpretability, select any entity node to inspect its local
          relational neighborhood up to 35 connected nodes.
        </div>
      </div>

      {/* Global Graph Statistics */}
      {loadingOverview ? (
        <LoadingState message="Querying global multi-relational graph metrics..." minHeight="120px" />
      ) : errorOverview ? (
        <ErrorState title="Graph Overview Error" message={errorOverview} />
      ) : overview ? (
        <div className="grid-cols-4">
          <MetricCard
            title="Total Graph Nodes"
            value={formatNumber(overview.totalNodes)}
            subtitle="Heterogeneous entities"
            icon={<Network size={20} />}
            accentColor="#38bdf8"
          />
          <MetricCard
            title="Relational Edges"
            value={formatNumber(overview.totalEdges)}
            subtitle="Multi-relational links"
            icon={<Layers size={20} />}
            accentColor="#a855f7"
          />
          <MetricCard
            title="Relation Types"
            value={overview.relationTypesCount}
            subtitle="Typed canonical edges"
            icon={<Layers size={20} />}
            accentColor="#f59e0b"
          />
          <MetricCard
            title="Feature Dimension"
            value={`${overview.featureDimension}D`}
            subtitle="Normalized node embedding"
            icon={<Network size={20} />}
            accentColor="#10b981"
          />
        </div>
      ) : null}

      {/* Subgraph Query Controls */}
      <Card title="Subgraph Neighborhood Query" subtitle="Center the interactive view on any entity in the network">
        <form
          onSubmit={handleSearchSubmit}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            flexWrap: 'wrap',
            marginTop: '8px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>Entity Type:</label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              style={{ minWidth: '150px' }}
            >
              <option value="application">Application</option>
              <option value="student">Student</option>
              <option value="company">Company</option>
              <option value="job">Job</option>
              <option value="skill">Skill</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1, minWidth: '240px' }}>
            <label style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>Entity ID:</label>
            <input
              type="text"
              placeholder="e.g. A00001, S1654, C014, J0263, Python"
              value={selectedId}
              onChange={(e) => setSelectedId(e.target.value)}
              style={{ width: '100%', fontFamily: 'var(--font-mono)' }}
            />
          </div>

          <button
            type="submit"
            disabled={loadingSubgraph}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '9px 18px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--color-primary-dark)',
              color: '#ffffff',
              fontSize: '0.86rem',
              fontWeight: 600,
              cursor: loadingSubgraph ? 'not-allowed' : 'pointer',
            }}
          >
            <Play size={15} />
            Render Subgraph
          </button>
        </form>

        {/* Quick Suggestion Chips */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '14px', flexWrap: 'wrap', fontSize: '0.78rem' }}>
          <span style={{ color: 'var(--text-muted)' }}>Quick Examples:</span>
          {[
            { type: 'application', id: 'A00001' },
            { type: 'application', id: 'A00002' },
            { type: 'student', id: 'S1654' },
            { type: 'company', id: 'C014' },
            { type: 'job', id: 'J0263' },
            { type: 'skill', id: 'Python' },
          ].map((ex) => (
            <button
              key={`${ex.type}-${ex.id}`}
              onClick={() => {
                setSelectedType(ex.type);
                setSelectedId(ex.id);
                fetchSubgraph(ex.type, ex.id);
              }}
              style={{
                padding: '3px 8px',
                borderRadius: '4px',
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-secondary)',
                fontFamily: 'var(--font-mono)',
              }}
            >
              {ex.id} ({ex.type})
            </button>
          ))}
        </div>
      </Card>

      {/* Interactive Subgraph Canvas */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>
            Interactive Subgraph Canvas
            {subgraph && (
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginLeft: '10px' }}>
                ({subgraph.nodesCount} nodes, {subgraph.linksCount} relations)
              </span>
            )}
          </h3>
          <GraphLegend />
        </div>

        {loadingSubgraph ? (
          <LoadingState message={`Fetching local neighborhood around ${selectedType} ${selectedId}...`} minHeight="480px" />
        ) : errorSubgraph ? (
          <ErrorState
            title="Neighborhood Fetch Failed"
            message={errorSubgraph}
            onRetry={() => fetchSubgraph(selectedType, selectedId)}
            minHeight="400px"
          />
        ) : subgraph ? (
          <SubgraphVisualizer
            data={subgraph}
            onNavigateToNode={handleNavigateToNode}
            height="540px"
          />
        ) : null}
      </div>
    </div>
  );
};
