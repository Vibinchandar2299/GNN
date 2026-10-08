import React from 'react';
import { Menu, Activity } from 'lucide-react';
import { useLocation } from 'react-router-dom';

interface HeaderProps {
  onToggleSidebar: () => void;
}

const ROUTE_TITLES: Record<string, { title: string; subtitle: string }> = {
  '/dashboard': {
    title: 'Research Dashboard',
    subtitle: 'System KPIs, dataset distribution, and recruitment cycles',
  },
  '/candidates': {
    title: 'Candidate Explorer',
    subtitle: 'Student academic performance, scores, and acquired skills',
  },
  '/companies': {
    title: 'Company Analytics',
    subtitle: 'Corporate recruiters, industry verticals, and hiring selection rates',
  },
  '/jobs': {
    title: 'Job Postings & Requirements',
    subtitle: 'Open roles, package offerings, and skill demand matrices',
  },
  '/skills': {
    title: 'Skill Taxonomy & Demand',
    subtitle: 'Supply vs. demand analysis across the 18 research skills',
  },
  '/applications': {
    title: 'Application Records',
    subtitle: 'Applicant interactions, predictive attributes, and outcomes',
  },
  '/graph': {
    title: 'Knowledge Graph Visualization',
    subtitle: 'Interactive multi-relational graph neighborhood explorer (5,977 nodes, 43,044 edges)',
  },
  '/trends': {
    title: 'Hiring Trends & Temporal Shifts',
    subtitle: 'Cycle progression and selection dynamics (2023–2026)',
  },
  '/model': {
    title: 'AMRG-GraphSAGE Research Benchmark',
    subtitle: 'Deep GNN architecture specifications, ablation metrics, and evaluation protocol',
  },
};

export const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  const location = useLocation();

  // Match root or prefix
  const pathKey = Object.keys(ROUTE_TITLES).find(
    (key) => location.pathname === key || (key !== '/dashboard' && location.pathname.startsWith(key))
  ) || '/dashboard';

  const { title, subtitle } = ROUTE_TITLES[pathKey] || {
    title: 'HireGraph AI',
    subtitle: 'Decision-Support Platform',
  };

  return (
    <header className="top-header">
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button
          onClick={onToggleSidebar}
          style={{
            display: 'none',
            padding: '8px',
            color: 'var(--text-primary)',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-elevated)',
          }}
          className="mobile-menu-btn"
          aria-label="Toggle menu"
        >
          <Menu size={20} />
        </button>

        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            {title}
          </h1>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            {subtitle}
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 12px',
            borderRadius: 'var(--radius-full)',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            fontSize: '0.78rem',
            color: 'var(--color-selected)',
            fontWeight: 500,
          }}
        >
          <Activity size={14} />
          <span>Spring Boot 3 Backend Online</span>
        </div>
      </div>
    </header>
  );
};
