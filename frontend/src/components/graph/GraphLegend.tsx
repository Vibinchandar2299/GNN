import React from 'react';
import { ENTITY_COLORS } from '../../utils/constants';

export const GraphLegend: React.FC = () => {
  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '14px',
        padding: '12px 16px',
        backgroundColor: 'var(--bg-elevated)',
        borderRadius: 'var(--radius-sm)',
        border: '1px solid var(--border-subtle)',
        fontSize: '0.8rem',
      }}
    >
      <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Entity Types:</span>
      {Object.entries(ENTITY_COLORS).map(([type, color]) => (
        <div key={type} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span
            style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: color.hex,
              display: 'inline-block',
              boxShadow: `0 0 6px ${color.hex}60`,
            }}
          />
          <span style={{ textTransform: 'capitalize', color: 'var(--text-primary)' }}>{type}</span>
        </div>
      ))}
    </div>
  );
};
