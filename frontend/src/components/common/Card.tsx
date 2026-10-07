import React from 'react';

interface CardProps {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  action,
  children,
  className = '',
  style,
}) => {
  return (
    <div className={`card ${className}`} style={style}>
      {(title || action) && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '16px',
            borderBottom: subtitle ? 'none' : '1px solid var(--border-subtle)',
            paddingBottom: subtitle ? '0' : '12px',
          }}
        >
          <div>
            {title && <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)' }}>{title}</h3>}
            {subtitle && <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '2px' }}>{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
};
