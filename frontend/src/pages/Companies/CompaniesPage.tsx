import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Building2, Filter } from 'lucide-react';
import { companyApi } from '../../api/companyApi';
import { Company } from '../../types/company';
import { PageResponse } from '../../types/common';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import { PaginationControls } from '../../components/common/PaginationControls';
import { SearchInput } from '../../components/common/SearchInput';
import { formatNumber, formatPercent, formatDecimal } from '../../utils/formatting';

export const CompaniesPage: React.FC = () => {
  const navigate = useNavigate();
  const [pageData, setPageData] = useState<PageResponse<Company> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [selectedIndustry, setSelectedIndustry] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const fetchCompanies = async (page: number, industry?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await companyApi.getCompanies({
        page,
        size: 15,
        industry: industry || undefined,
      });
      setPageData(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch companies.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompanies(currentPage, selectedIndustry);
  }, [currentPage, selectedIndustry]);

  const displayedCompanies = pageData?.content.filter((c) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      c.companyName.toLowerCase().includes(q) ||
      c.companyId.toLowerCase().includes(q) ||
      c.industry.toLowerCase().includes(q)
    );
  }) || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Search & Filter Bar */}
      <div
        className="card"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
          padding: '16px 20px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
          <SearchInput
            placeholder="Search company name or ID..."
            value={searchQuery}
            onChange={(q) => setSearchQuery(q)}
          />

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Filter size={16} style={{ color: 'var(--text-muted)' }} />
            <select
              value={selectedIndustry}
              onChange={(e) => {
                setSelectedIndustry(e.target.value);
                setCurrentPage(0);
              }}
              style={{ minWidth: '180px' }}
            >
              <option value="">All Industries</option>
              <option value="IT Services">IT Services</option>
              <option value="Product">Product</option>
              <option value="Finance">Finance</option>
              <option value="Consulting">Consulting</option>
              <option value="Manufacturing">Manufacturing</option>
            </select>
          </div>
        </div>

        {pageData && (
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Showing <strong>{displayedCompanies.length}</strong> of{' '}
            <strong>{formatNumber(pageData.totalElements)}</strong> companies
          </div>
        )}
      </div>

      {/* Main Table Card */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <LoadingState message="Fetching corporate recruiter roster..." />
        ) : error ? (
          <ErrorState
            title="Company Directory Error"
            message={error}
            onRetry={() => fetchCompanies(currentPage, selectedIndustry)}
          />
        ) : displayedCompanies.length === 0 ? (
          <EmptyState
            title="No Companies Found"
            message="No corporate recruiter profiles correspond to the specified filter criteria."
            actionText="Reset Filters"
            onAction={() => {
              setSelectedIndustry('');
              setSearchQuery('');
              setCurrentPage(0);
            }}
          />
        ) : (
          <>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.86rem' }}>
                <thead>
                  <tr style={{ backgroundColor: 'var(--bg-elevated)', borderBottom: '1px solid var(--border-subtle)' }}>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Company ID</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Company Name</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Industry</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Company Size</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Selection Rate</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Avg Selected CGPA</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Total Apps</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600, textAlign: 'right' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {displayedCompanies.map((c) => (
                    <tr
                      key={c.companyId}
                      style={{
                        borderBottom: '1px solid var(--border-subtle)',
                        transition: 'background-color 0.15s ease',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--bg-card-hover)')}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#f59e0b' }}>
                        {c.companyId}
                      </td>
                      <td style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-primary)' }}>
                        {c.companyName}
                      </td>
                      <td style={{ padding: '14px 16px', color: 'var(--text-secondary)' }}>
                        {c.industry}
                      </td>
                      <td style={{ padding: '14px 16px', color: 'var(--text-secondary)' }}>
                        {c.companySize}
                      </td>
                      <td style={{ padding: '14px 16px', fontWeight: 600, fontFamily: 'var(--font-mono)', color: 'var(--color-primary)' }}>
                        {formatPercent(c.historicalSelectionRate)}
                      </td>
                      <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)' }}>
                        {formatDecimal(c.historicalAverageSelectedCgpa, 2)}
                      </td>
                      <td style={{ padding: '14px 16px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
                        {formatNumber(c.totalApplications)}
                      </td>
                      <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                        <button
                          onClick={() => navigate(`/companies/${c.companyId}`)}
                          style={{
                            padding: '6px 12px',
                            borderRadius: 'var(--radius-sm)',
                            backgroundColor: 'var(--bg-elevated)',
                            border: '1px solid var(--border-subtle)',
                            color: 'var(--color-primary)',
                            fontSize: '0.8rem',
                            fontWeight: 500,
                          }}
                        >
                          View Profile
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {pageData && (
              <PaginationControls
                currentPage={currentPage}
                totalPages={pageData.totalPages}
                totalElements={pageData.totalElements}
                onPageChange={(p) => setCurrentPage(p)}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
};
