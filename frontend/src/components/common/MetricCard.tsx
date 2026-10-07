import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  accentColor?: string;
  trend?: string;
  isPositive?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  accentColor = '#38bdf8',
  trend,
  isPositive,
}) => {
  return (
    <div
      className="card"
      style={{
        position: 'relative',
        overflow: 'hidden',
        borderLeft: `3px solid ${accentColor}`,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {title}
          </span>
          <div style={{ fontSize: '1.85rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>
            {value}
          </div>
        </div>
        {icon && (
          <div
            style={{
              padding: '10px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--bg-elevated)',
              color: accentColor,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </div>
        )}
      </div>

      {(subtitle || trend) && (
        <div style={{ marginTop: '12px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem' }}>
          {trend && (
            <span
              style={{
                fontWeight: 600,
                color: isPositive ? 'var(--color-selected)' : 'var(--color-rejected)',
              }}
            >
              {trend}
            </span>
          )}
          {subtitle && <span style={{ color: 'var(--text-muted)' }}>{subtitle}</span>}
        </div>
      )}
    </div>
  );
};
