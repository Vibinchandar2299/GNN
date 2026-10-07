import React, { useState, useEffect } from 'react';
import { Search, X } from 'lucide-react';

interface SearchInputProps {
  placeholder?: string;
  value: string;
  onChange: (val: string) => void;
  debounceMs?: number;
}

export const SearchInput: React.FC<SearchInputProps> = ({
  placeholder = 'Search records...',
  value,
  onChange,
  debounceMs = 300,
}) => {
  const [internalValue, setInternalValue] = useState(value);

  useEffect(() => {
    setInternalValue(value);
  }, [value]);

  useEffect(() => {
    const handler = setTimeout(() => {
      if (internalValue !== value) {
        onChange(internalValue);
      }
    }, debounceMs);

    return () => clearTimeout(handler);
  }, [internalValue, debounceMs, onChange, value]);

  return (
    <div style={{ position: 'relative', display: 'flex', alignItems: 'center', width: '100%', maxWidth: '360px' }}>
      <Search
        size={16}
        style={{
          position: 'absolute',
          left: '12px',
          color: 'var(--text-muted)',
          pointerEvents: 'none',
        }}
      />
      <input
        type="text"
        placeholder={placeholder}
        value={internalValue}
        onChange={(e) => setInternalValue(e.target.value)}
        style={{
          width: '100%',
          paddingLeft: '36px',
          paddingRight: internalValue ? '32px' : '12px',
          height: '38px',
          backgroundColor: 'var(--bg-surface)',
          borderRadius: 'var(--radius-sm)',
          fontSize: '0.86rem',
        }}
      />
      {internalValue && (
        <button
          onClick={() => {
            setInternalValue('');
            onChange('');
          }}
          style={{
            position: 'absolute',
            right: '10px',
            color: 'var(--text-muted)',
            display: 'flex',
            alignItems: 'center',
          }}
          title="Clear search"
        >
          <X size={14} />
        </button>
      )}
    </div>
  );
};
