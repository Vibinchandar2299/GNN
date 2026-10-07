import React from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  minHeight?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Unable to Load Data',
  message = 'A connection or processing error occurred while fetching information from the Spring Boot backend.',
  onRetry,
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
        gap: '14px',
        minHeight,
        textAlign: 'center',
        padding: '32px',
        borderColor: 'rgba(244, 63, 94, 0.4)',
        backgroundColor: 'rgba(244, 63, 94, 0.04)',
      }}
    >
      <div
        style={{
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          backgroundColor: 'rgba(244, 63, 94, 0.15)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--color-rejected)',
        }}
      >
        <AlertTriangle size={24} />
      </div>
      <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
        {title}
      </h3>
      <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', maxWidth: '460px' }}>
        {message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            marginTop: '8px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 18px',
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--color-primary)',
            fontSize: '0.85rem',
            fontWeight: 500,
            transition: 'background-color 0.15s ease',
          }}
        >
          <RotateCcw size={16} />
          Retry Request
        </button>
      )}
    </div>
  );
};
