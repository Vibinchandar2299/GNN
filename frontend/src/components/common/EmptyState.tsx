import React from 'react';
import { Database } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  message?: string;
  actionText?: string;
  onAction?: () => void;
  minHeight?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No Records Found',
  message = 'No matching hiring or applicant records correspond to the specified criteria.',
  actionText,
  onAction,
  minHeight = '240px',
}) => {
  return (
    <div
      className="card"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '12px',
        minHeight,
        textAlign: 'center',
        padding: '32px',
        color: 'var(--text-secondary)',
      }}
    >
      <div
        style={{
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          backgroundColor: 'var(--bg-elevated)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--text-muted)',
        }}
      >
        <Database size={22} />
      </div>
      <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)' }}>
        {title}
      </h3>
      <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)', maxWidth: '420px' }}>
        {message}
      </p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          style={{
            marginTop: '8px',
            padding: '8px 16px',
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--color-primary)',
            fontSize: '0.85rem',
            fontWeight: 500,
          }}
        >
          {actionText}
        </button>
      )}
    </div>
  );
};
