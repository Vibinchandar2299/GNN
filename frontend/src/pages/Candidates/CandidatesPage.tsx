import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Filter } from 'lucide-react';
import { candidateApi } from '../../api/candidateApi';
import { Candidate } from '../../types/candidate';
import { PageResponse } from '../../types/common';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import { PaginationControls } from '../../components/common/PaginationControls';
import { SearchInput } from '../../components/common/SearchInput';
import { formatNumber, formatDecimal } from '../../utils/formatting';

export const CandidatesPage: React.FC = () => {
  const navigate = useNavigate();
  const [pageData, setPageData] = useState<PageResponse<Candidate> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [selectedDept, setSelectedDept] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const fetchCandidates = async (page: number, dept?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await candidateApi.getCandidates({
        page,
        size: 15,
        department: dept || undefined,
      });
      setPageData(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load candidates.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates(currentPage, selectedDept);
  }, [currentPage, selectedDept]);

  const handleDeptChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedDept(e.target.value);
    setCurrentPage(0);
  };

  // Client-side search within current page or by ID
  const displayedCandidates = pageData?.content.filter((c) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      c.studentId.toLowerCase().includes(q) ||
      c.department.toLowerCase().includes(q)
    );
  }) || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Controls Bar */}
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
            placeholder="Search student ID (e.g. S0001)..."
            value={searchQuery}
            onChange={(q) => setSearchQuery(q)}
          />

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Filter size={16} style={{ color: 'var(--text-muted)' }} />
            <select
              value={selectedDept}
              onChange={handleDeptChange}
              style={{ minWidth: '180px' }}
            >
              <option value="">All Departments</option>
              <option value="Computer Science">Computer Science</option>
              <option value="Information Technology">Information Technology</option>
              <option value="Electronics">Electronics</option>
              <option value="Mechanical">Mechanical</option>
              <option value="Civil">Civil</option>
            </select>
          </div>
        </div>

        {pageData && (
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Showing <strong>{displayedCandidates.length}</strong> of{' '}
            <strong>{formatNumber(pageData.totalElements)}</strong> candidates
          </div>
        )}
      </div>

      {/* Main Table Card */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <LoadingState message="Fetching student records from database..." />
        ) : error ? (
          <ErrorState
            title="Candidate Roster Error"
            message={error}
            onRetry={() => fetchCandidates(currentPage, selectedDept)}
          />
        ) : displayedCandidates.length === 0 ? (
          <EmptyState
            title="No Candidates Found"
            message="No candidate records match the selected filters."
            actionText="Reset Filters"
            onAction={() => {
              setSelectedDept('');
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
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Student ID</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Department</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>CGPA</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Backlogs</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Coding / Aptitude</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Projects</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Acquired Skills</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600, textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {displayedCandidates.map((c) => (
                    <tr
                      key={c.studentId}
                      style={{
                        borderBottom: '1px solid var(--border-subtle)',
                        transition: 'background-color 0.15s ease',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--bg-card-hover)')}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--color-primary)' }}>
                        {c.studentId}
                      </td>
                      <td style={{ padding: '14px 16px', color: 'var(--text-primary)' }}>
                        {c.department}
                      </td>
                      <td style={{ padding: '14px 16px', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
                        {formatDecimal(c.cgpa, 2)}
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <span
                          style={{
                            color: c.backlogs === 0 ? 'var(--color-selected)' : 'var(--color-rejected)',
                            fontWeight: 600,
                          }}
                        >
                          {c.backlogs}
                        </span>
                      </td>
                      <td style={{ padding: '14px 16px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
                        {formatDecimal(c.codingScorePre, 1)} / {formatDecimal(c.aptitudeScorePre, 1)}
                      </td>
                      <td style={{ padding: '14px 16px', color: 'var(--text-primary)' }}>
                        {c.projectsCount} proj • {c.internshipsCount} intern
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', maxWidth: '280px' }}>
                          {c.skills?.slice(0, 3).map((s) => (
                            <span
                              key={s}
                              style={{
                                padding: '2px 8px',
                                borderRadius: '4px',
                                fontSize: '0.72rem',
                                backgroundColor: 'rgba(56, 189, 248, 0.1)',
                                color: '#38bdf8',
                                border: '1px solid rgba(56, 189, 248, 0.25)',
                              }}
                            >
                              {s}
                            </span>
                          ))}
                          {(c.skills?.length || 0) > 3 && (
                            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                              +{c.skills.length - 3} more
                            </span>
                          )}
                        </div>
                      </td>
                      <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                        <button
                          onClick={() => navigate(`/candidates/${c.studentId}`)}
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
