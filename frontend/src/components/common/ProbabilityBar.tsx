import React from 'react';

interface ProbabilityBarProps {
  probability: number; // between 0.0 and 1.0 or 0 to 100
  threshold?: number;
  showLabel?: boolean;
}

export const ProbabilityBar: React.FC<ProbabilityBarProps> = ({
  probability,
  threshold = 0.5,
  showLabel = true,
}) => {
  const normProb = probability <= 1 && probability >= 0 ? probability : probability / 100;
  const pct = (normProb * 100).toFixed(1);
  const isSelected = normProb >= threshold;

  const barColor = isSelected ? 'var(--color-selected)' : 'var(--color-rejected)';
  const glow = isSelected ? 'var(--color-selected-glow)' : 'var(--color-rejected-glow)';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', width: '100%' }}>
      {showLabel && (
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
          <span style={{ color: 'var(--text-secondary)' }}>Estimated Probability</span>
          <span style={{ fontWeight: 700, color: barColor, fontFamily: 'var(--font-mono)' }}>
            {pct}%
          </span>
        </div>
      )}
      <div
        style={{
          width: '100%',
          height: '10px',
          backgroundColor: 'var(--bg-input)',
          borderRadius: 'var(--radius-full)',
          overflow: 'hidden',
          border: '1px solid var(--border-subtle)',
          position: 'relative',
        }}
      >
        <div
          style={{
            width: `${pct}%`,
            height: '100%',
            backgroundColor: barColor,
            borderRadius: 'var(--radius-full)',
            boxShadow: `0 0 10px ${glow}`,
            transition: 'width 0.6s cubic-bezier(0.16, 1, 0.3, 1)',
          }}
        />
        {/* Decision threshold indicator at 50% */}
        <div
          style={{
            position: 'absolute',
            left: '50%',
            top: 0,
            bottom: 0,
            width: '2px',
            backgroundColor: 'var(--text-muted)',
            opacity: 0.4,
          }}
          title="Decision threshold (0.50)"
        />
      </div>
    </div>
  );
};
