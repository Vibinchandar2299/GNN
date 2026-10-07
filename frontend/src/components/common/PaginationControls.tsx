import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { formatNumber } from '../../utils/formatting';

interface PaginationControlsProps {
  currentPage: number; // 0-indexed
  totalPages: number;
  totalElements?: number;
  pageSize?: number;
  onPageChange: (newPage: number) => void;
}

export const PaginationControls: React.FC<PaginationControlsProps> = ({
  currentPage,
  totalPages,
  totalElements,
  onPageChange,
}) => {
  if (totalPages <= 1 && (!totalElements || totalElements <= 0)) {
    return null;
  }

  const hasPrevious = currentPage > 0;
  const hasNext = currentPage < totalPages - 1;

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 16px',
        borderTop: '1px solid var(--border-subtle)',
        fontSize: '0.84rem',
        color: 'var(--text-secondary)',
      }}
    >
      <div>
        {totalElements !== undefined && (
          <span>
            Total: <strong style={{ color: 'var(--text-primary)' }}>{formatNumber(totalElements)}</strong> records
          </span>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span>
          Page <strong style={{ color: 'var(--text-primary)' }}>{currentPage + 1}</strong> of{' '}
          <strong style={{ color: 'var(--text-primary)' }}>{Math.max(totalPages, 1)}</strong>
        </span>

        <div style={{ display: 'flex', gap: '4px' }}>
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={!hasPrevious}
            style={{
              padding: '6px 10px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              backgroundColor: 'var(--bg-elevated)',
              color: hasPrevious ? 'var(--text-primary)' : 'var(--text-muted)',
              cursor: hasPrevious ? 'pointer' : 'not-allowed',
              opacity: hasPrevious ? 1 : 0.5,
              display: 'flex',
              alignItems: 'center',
            }}
            title="Previous page"
          >
            <ChevronLeft size={16} />
          </button>

          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={!hasNext}
            style={{
              padding: '6px 10px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              backgroundColor: 'var(--bg-elevated)',
              color: hasNext ? 'var(--text-primary)' : 'var(--text-muted)',
              cursor: hasNext ? 'pointer' : 'not-allowed',
              opacity: hasNext ? 1 : 0.5,
              display: 'flex',
              alignItems: 'center',
            }}
            title="Next page"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};
