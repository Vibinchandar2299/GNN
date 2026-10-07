import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Filter } from 'lucide-react';
import { applicationApi } from '../../api/applicationApi';
import { Application } from '../../types/application';
import { PageResponse } from '../../types/common';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import { PaginationControls } from '../../components/common/PaginationControls';
import { SearchInput } from '../../components/common/SearchInput';
import { StatusBadge } from '../../components/common/StatusBadge';
import { DisclaimerCard } from '../../components/common/DisclaimerCard';
import { formatNumber, formatPercent } from '../../utils/formatting';

export const ApplicationsPage: React.FC = () => {
  const navigate = useNavigate();
  const [pageData, setPageData] = useState<PageResponse<Application> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [selectedCycle, setSelectedCycle] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const fetchApplications = async (page: number, cycle?: string, status?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await applicationApi.getApplications({
        page,
        size: 15,
        cycle: cycle ? parseInt(cycle, 10) : undefined,
        finalStatus: status !== '' ? parseInt(status, 10) : undefined,
      });
      setPageData(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch application records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications(currentPage, selectedCycle, selectedStatus);
  }, [currentPage, selectedCycle, selectedStatus]);

  const displayedApps = pageData?.content.filter((a) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      a.applicationId.toLowerCase().includes(q) ||
      a.studentId.toLowerCase().includes(q) ||
      a.companyId.toLowerCase().includes(q) ||
      a.jobId.toLowerCase().includes(q)
    );
  }) || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <DisclaimerCard customText="Applications represent historical recruitment drives. Running model prediction executes live forward-pass inference on the frozen AMRG-GraphSAGE model." />

      {/* Filter and Search Bar */}
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1, flexWrap: 'wrap' }}>
          <SearchInput
            placeholder="Search App ID, Student, Company, Job..."
            value={searchQuery}
            onChange={(q) => setSearchQuery(q)}
          />

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Filter size={16} style={{ color: 'var(--text-muted)' }} />
            <select
              value={selectedCycle}
              onChange={(e) => {
                setSelectedCycle(e.target.value);
                setCurrentPage(0);
              }}
              style={{ minWidth: '140px' }}
            >
              <option value="">All Cycles</option>
              <option value="2023">Cycle 2023</option>
              <option value="2024">Cycle 2024</option>
              <option value="2025">Cycle 2025</option>
              <option value="2026">Cycle 2026</option>
            </select>

            <select
              value={selectedStatus}
              onChange={(e) => {
                setSelectedStatus(e.target.value);
                setCurrentPage(0);
              }}
              style={{ minWidth: '150px' }}
            >
              <option value="">All Outcomes</option>
              <option value="1">Historical: Selected</option>
              <option value="0">Historical: Rejected</option>
            </select>
          </div>
        </div>

        {pageData && (
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Showing <strong>{displayedApps.length}</strong> of{' '}
            <strong>{formatNumber(pageData.totalElements)}</strong> applications
          </div>
        )}
      </div>

      {/* Applications Table Card */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <LoadingState message="Fetching application records from database..." />
        ) : error ? (
          <ErrorState
            title="Applications Catalog Error"
            message={error}
            onRetry={() => fetchApplications(currentPage, selectedCycle, selectedStatus)}
          />
        ) : displayedApps.length === 0 ? (
          <EmptyState
            title="No Applications Found"
            message="No applications correspond to the selected cycle and filter criteria."
            actionText="Reset Filters"
            onAction={() => {
              setSelectedCycle('');
              setSelectedStatus('');
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
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>App ID</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Student ID</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Company ID</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Job ID</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Cycle</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Historical Truth</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600 }}>Model Estimate</th>
                    <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 600, textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {displayedApps.map((a) => (
                    <tr
                      key={a.applicationId}
                      style={{
                        borderBottom: '1px solid var(--border-subtle)',
                        transition: 'background-color 0.15s ease',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--bg-card-hover)')}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--color-primary)' }}>
                        {a.applicationId}
                      </td>
                      <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                        {a.studentId}
                      </td>
                      <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                        {a.companyId}
                      </td>
                      <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                        {a.jobId}
                      </td>
                      <td style={{ padding: '14px 16px', color: 'var(--text-primary)' }}>
                        Cycle {a.cycle}
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <StatusBadge status={a.finalStatus} />
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        {a.latestPrediction ? (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <StatusBadge status={a.latestPrediction.predictedStatus} isModelEstimate />
                            <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
                              ({formatPercent(a.latestPrediction.estimatedProbability)})
                            </span>
                          </div>
                        ) : (
                          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Not estimated yet</span>
                        )}
                      </td>
                      <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                        <button
                          onClick={() => navigate(`/applications/${a.applicationId}`)}
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
                          Inspect & Predict
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
