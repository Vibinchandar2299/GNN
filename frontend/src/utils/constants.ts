export const APP_TITLE = 'HireGraph AI';
export const APP_SUBTITLE = 'Explainable Hiring Pattern Analysis using AMRG-GraphSAGE';
export const RESEARCH_TITLE = 'An Explainable AMRG-GraphSAGE Framework for Hiring Pattern Analysis under Evolving Job Requirements';

export const DISCLAIMER_TEXT =
  'This prediction represents an AI-generated decision-support estimate based on historical hiring patterns and is not a guaranteed hiring decision.';

export const DECISION_SUPPORT_LABEL = 'Model-estimated outcome';

export const ENTITY_COLORS: Record<string, { bg: string; border: string; text: string; hex: string }> = {
  application: {
    bg: 'rgba(14, 165, 233, 0.15)',
    border: 'rgba(14, 165, 233, 0.5)',
    text: '#38bdf8',
    hex: '#0ea5e9',
  },
  student: {
    bg: 'rgba(16, 185, 129, 0.15)',
    border: 'rgba(16, 185, 129, 0.5)',
    text: '#34d399',
    hex: '#10b981',
  },
  company: {
    bg: 'rgba(245, 158, 11, 0.15)',
    border: 'rgba(245, 158, 11, 0.5)',
    text: '#fbbf24',
    hex: '#f59e0b',
  },
  job: {
    bg: 'rgba(139, 92, 246, 0.15)',
    border: 'rgba(139, 92, 246, 0.5)',
    text: '#a78bfa',
    hex: '#8b5cf6',
  },
  skill: {
    bg: 'rgba(244, 63, 94, 0.15)',
    border: 'rgba(244, 63, 94, 0.5)',
    text: '#fb7185',
    hex: '#f43f5e',
  },
};
