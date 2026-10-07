import React from 'react';
import { AlertCircle } from 'lucide-react';
import { DISCLAIMER_TEXT } from '../../utils/constants';

interface DisclaimerCardProps {
  customText?: string;
  style?: React.CSSProperties;
}

export const DisclaimerCard: React.FC<DisclaimerCardProps> = ({ customText, style }) => {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px',
        padding: '14px 18px',
        borderRadius: 'var(--radius-md)',
        backgroundColor: 'rgba(245, 158, 11, 0.08)',
        border: '1px solid rgba(245, 158, 11, 0.3)',
        color: '#fef3c7',
        fontSize: '0.84rem',
        lineHeight: 1.5,
        ...style,
      }}
    >
      <AlertCircle size={18} style={{ color: 'var(--color-warning)', flexShrink: 0, marginTop: '2px' }} />
      <div>
        <strong style={{ color: 'var(--color-warning)', marginRight: '6px' }}>Decision-Support Notice:</strong>
        {customText || DISCLAIMER_TEXT}
      </div>
    </div>
  );
};
