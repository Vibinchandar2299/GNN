import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Network, Home, ArrowLeft } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
        textAlign: 'center',
        gap: '20px',
        padding: '32px',
      }}
    >
      <div
        style={{
          width: '72px',
          height: '72px',
          borderRadius: '50%',
          backgroundColor: 'rgba(56, 189, 248, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--color-primary)',
          border: '1px solid var(--border-focus)',
        }}
      >
        <Network size={36} />
      </div>

      <h1 style={{ fontSize: '3rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
        404
      </h1>
      <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
        Research Node or Route Not Found
      </h2>
      <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', maxWidth: '440px' }}>
        The requested path does not match any valid research dashboard view, entity catalog, or model benchmark.
      </p>

      <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
        <button
          onClick={() => navigate(-1)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 18px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-subtle)',
            color: 'var(--text-primary)',
            fontSize: '0.88rem',
            fontWeight: 500,
          }}
        >
          <ArrowLeft size={16} /> Go Back
        </button>

        <button
          onClick={() => navigate('/dashboard')}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 18px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--color-primary-dark)',
            color: '#ffffff',
            fontSize: '0.88rem',
            fontWeight: 600,
          }}
        >
          <Home size={16} /> Dashboard
        </button>
      </div>
    </div>
  );
};
