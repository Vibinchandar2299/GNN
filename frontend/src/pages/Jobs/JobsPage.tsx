import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Filter } from 'lucide-react';
import { jobApi } from '../../api/jobApi';
import { Job } from '../../types/job';
import { PageResponse } from '../../types/common';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import { PaginationControls } from '../../components/common/PaginationControls';
import { SearchInput } from '../../components/common/SearchInput';
import { formatNumber, formatCurrencyLpa, formatDecimal } from '../../utils/formatting';

export const JobsPage: React.FC = () => {
  const navigate = useNavigate();
  const [pageData, setPageData] = useState<PageResponse<Job> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [selectedDomain, setSelectedDomain] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const fetchJobs = async (page: number, domain?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await jobApi.getJobs({
        page,
        size: 15,
        domain: domain || undefined,
      });
      setPageData(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch jobs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs(currentPage, selectedDomain);
  }, [currentPage, selectedDomain]);

  const displayedJobs = pageData?.content.filter((j) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      j.jobTitle.toLowerCase().includes(q) ||
      j.jobId.toLowerCase().includes(q) ||
      j.jobDomain.toLowerCase().includes(q)
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
            placeholder="Search job title or ID..."
            value={searchQuery}
            onChange={(q) => setSearchQuery(q)}
          />

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Filter size={16} style={{ color: 'var(--text-muted)' }} />
            <select
              value={selectedDomain}
              onChange={(e) => {
                setSelectedDomain(e.target.value);
                setCurrentPage(0);
              }}
              style={{ minWidth: '180px' }}
            >
              <option value="">All Job Domains</option>
              <option value="Software Development">Software Development</option>
              <option value="Data Science">Data Science</option>
              <option value="Machine Learning">Machine Learning</option>
              <option value="DevOps & Cloud">DevOps & Cloud</option>
              <option value="Cybersecurity">Cybersecurity</option>
              <option value="Consulting">Consulting</option>
            </select>
          </div>
        </div>

        {pageData && (
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Showing <strong>{displayedJobs.length}</strong> of{' '}
            <strong>{formatNumber(pageData.totalElements)}</strong> jobs
          </div>
        )}
      </div>

      {/* Main Table Card */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <LoadingState message="Fetching active job postings catalog..." />
        ) : error ? (
          <ErrorState
            title="Jobs Catalog Error"
            message={error}
            onRetry={() => fetchJobs(currentPage, selectedDomain)}
          />
        ) : displayedJobs.length === 0 ? (
          <EmptyState
            title="No Jobs Found"
            message="No job specifications match the requested filter criteria."
            actionText="Reset Filters"
            onAction={() => {
              setSelectedDomain('');
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
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Job ID</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Job Title</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Domain</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Min CGPA</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Experience Req.</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Salary Package</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Required Skills</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600, textAlign: 'right' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {displayedJobs.map((j) => (
                    <tr
                      key={j.jobId}
                      style={{
                        borderBottom: '1px solid var(--border-subtle)',
                        transition: 'background-color 0.15s ease',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--bg-card-hover)')}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#a855f7' }}>
                        {j.jobId}
                      </td>
                      <td style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-primary)' }}>
                        {j.jobTitle}
                      </td>
                      <td style={{ padding: '14px 16px', color: 'var(--text-secondary)' }}>
                        {j.jobDomain}
                      </td>
                      <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)' }}>
                        {formatDecimal(j.minimumCgpa, 2)}
                      </td>
                      <td style={{ padding: '14px 16px', color: 'var(--text-secondary)' }}>
                        {j.experienceRequiredMonths} months
                      </td>
                      <td style={{ padding: '14px 16px', fontWeight: 600, fontFamily: 'var(--font-mono)', color: 'var(--color-selected)' }}>
                        {formatCurrencyLpa(j.salaryLpa)}
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', maxWidth: '280px' }}>
                          {j.requiredSkills?.slice(0, 3).map((s) => (
                            <span
                              key={s}
                              style={{
                                padding: '2px 8px',
                                borderRadius: '4px',
                                fontSize: '0.72rem',
                                backgroundColor: 'rgba(168, 85, 247, 0.1)',
                                color: '#c084fc',
                                border: '1px solid rgba(168, 85, 247, 0.25)',
                              }}
                            >
                              {s}
                            </span>
                          ))}
                          {(j.requiredSkills?.length || 0) > 3 && (
                            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                              +{j.requiredSkills.length - 3} more
                            </span>
                          )}
                        </div>
                      </td>
                      <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                        <button
                          onClick={() => navigate(`/jobs/${j.jobId}`)}
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
                          View Spec
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
