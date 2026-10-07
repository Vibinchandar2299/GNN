import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Building2,
  Briefcase,
  Layers,
  FileText,
  Network,
  TrendingUp,
  BrainCircuit,
  ShieldAlert,
} from 'lucide-react';
import { APP_TITLE, APP_SUBTITLE } from '../../utils/constants';

interface SidebarProps {
  isOpen: boolean;
  onCloseMobile: () => void;
}

const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/candidates', label: 'Candidates', icon: Users },
  { path: '/companies', label: 'Companies', icon: Building2 },
  { path: '/jobs', label: 'Jobs', icon: Briefcase },
  { path: '/skills', label: 'Skills', icon: Layers },
  { path: '/applications', label: 'Applications', icon: FileText },
  { path: '/graph', label: 'Knowledge Graph', icon: Network },
  { path: '/trends', label: 'Hiring Trends', icon: TrendingUp },
  { path: '/model', label: 'Model Research', icon: BrainCircuit },
];

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onCloseMobile }) => {
  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      {/* Brand Header */}
      <div
        style={{
          padding: '24px 20px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          flexDirection: 'column',
          gap: '4px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              backgroundColor: 'rgba(56, 189, 248, 0.15)',
              border: '1px solid var(--border-focus)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--color-primary)',
            }}
          >
            <Network size={20} />
          </div>
          <span style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
            {APP_TITLE}
          </span>
        </div>
        <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', lineHeight: 1.3, marginTop: '4px' }}>
          {APP_SUBTITLE}
        </span>
      </div>

      {/* Navigation Links */}
      <nav style={{ padding: '16px 12px', flex: 1, overflowY: 'auto' }}>
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  onClick={onCloseMobile}
                  style={({ isActive }) => ({
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '10px 14px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.88rem',
                    fontWeight: isActive ? 600 : 500,
                    color: isActive ? 'var(--color-primary)' : 'var(--text-secondary)',
                    backgroundColor: isActive ? 'rgba(56, 189, 248, 0.1)' : 'transparent',
                    borderLeft: isActive ? '3px solid var(--color-primary)' : '3px solid transparent',
                    transition: 'all 0.15s ease',
                  })}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer Info / Disclaimer */}
      <div
        style={{
          padding: '16px 20px',
          borderTop: '1px solid var(--border-subtle)',
          fontSize: '0.72rem',
          color: 'var(--text-muted)',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-warning)' }}>
          <ShieldAlert size={14} />
          <span style={{ fontWeight: 600 }}>Decision-Support Engine</span>
        </div>
        <p>AMRG-GraphSAGE v1 (Research Artifact)</p>
        <p style={{ opacity: 0.8 }}>Spring Boot 3 + PostgreSQL + FastAPI</p>
      </div>
    </aside>
  );
};
