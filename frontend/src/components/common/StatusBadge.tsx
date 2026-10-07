import React from 'react';

interface StatusBadgeProps {
  status: string | number | undefined | null;
  isModelEstimate?: boolean;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, isModelEstimate = false }) => {
  const isSelected =
    status === 1 ||
    status === '1' ||
    status === 'SELECTED' ||
    status === 'Selected';

  const isRejected =
    status === 0 ||
    status === '0' ||
    status === 'REJECTED' ||
    status === 'Rejected';

  const label = isSelected ? 'SELECTED' : isRejected ? 'REJECTED' : 'UNKNOWN';

  const color = isSelected ? 'var(--color-selected)' : 'var(--color-rejected)';
  const bg = isSelected ? 'var(--color-selected-glow)' : 'var(--color-rejected-glow)';

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '3px 10px',
        borderRadius: 'var(--radius-full)',
        fontSize: '0.78rem',
        fontWeight: 600,
        letterSpacing: '0.04em',
        color: color,
        backgroundColor: bg,
        border: `1px solid ${color}40`,
      }}
    >
      <span
        style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          backgroundColor: color,
        }}
      />
      {isModelEstimate && (
        <span style={{ opacity: 0.8, fontSize: '0.7rem', fontWeight: 500 }}>EST:</span>
      )}
      {label}
    </span>
  );
};
