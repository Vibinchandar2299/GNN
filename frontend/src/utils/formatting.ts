export const formatNumber = (num: number | undefined | null): string => {
  if (num === undefined || num === null) return '0';
  return new Intl.NumberFormat('en-US').format(num);
};

export const formatPercent = (val: number | undefined | null, decimals: number = 1): string => {
  if (val === undefined || val === null) return '0.0%';
  // If value is between 0 and 1, multiply by 100
  const pct = val <= 1 && val >= 0 ? val * 100 : val;
  return `${pct.toFixed(decimals)}%`;
};

export const formatDecimal = (val: number | undefined | null, decimals: number = 4): string => {
  if (val === undefined || val === null) return '-';
  return val.toFixed(decimals);
};

export const formatCurrencyLpa = (val: number | undefined | null): string => {
  if (val === undefined || val === null) return '-';
  return `₹${val.toFixed(1)} LPA`;
};

export const getStatusLabel = (status: number | string | undefined | null): string => {
  if (status === 1 || status === 'SELECTED' || status === 'Selected') return 'SELECTED';
  if (status === 0 || status === 'REJECTED' || status === 'Rejected') return 'REJECTED';
  return 'UNKNOWN';
};
