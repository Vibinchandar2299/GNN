package com.hiregraph.dto.response;

public class IngestionResultResponse {
    private String status;
    private long applicationsCount;
    private long studentsCount;
    private long companiesCount;
    private long jobsCount;
    private long skillsCount;
    private long selectedCount;
    private long rejectedCount;
    private String message;

    public IngestionResultResponse() {}

    public IngestionResultResponse(String status, long applicationsCount, long studentsCount,
                                   long companiesCount, long jobsCount, long skillsCount,
                                   long selectedCount, long rejectedCount, String message) {
        this.status = status;
        this.applicationsCount = applicationsCount;
        this.studentsCount = studentsCount;
        this.companiesCount = companiesCount;
        this.jobsCount = jobsCount;
        this.skillsCount = skillsCount;
        this.selectedCount = selectedCount;
        this.rejectedCount = rejectedCount;
        this.message = message;
    }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public long getApplicationsCount() { return applicationsCount; }
    public void setApplicationsCount(long applicationsCount) { this.applicationsCount = applicationsCount; }

    public long getStudentsCount() { return studentsCount; }
    public void setStudentsCount(long studentsCount) { this.studentsCount = studentsCount; }

    public long getCompaniesCount() { return companiesCount; }
    public void setCompaniesCount(long companiesCount) { this.companiesCount = companiesCount; }

    public long getJobsCount() { return jobsCount; }
    public void setJobsCount(long jobsCount) { this.jobsCount = jobsCount; }

    public long getSkillsCount() { return skillsCount; }
    public void setSkillsCount(long skillsCount) { this.skillsCount = skillsCount; }

    public long getSelectedCount() { return selectedCount; }
    public void setSelectedCount(long selectedCount) { this.selectedCount = selectedCount; }

    public long getRejectedCount() { return rejectedCount; }
    public void setRejectedCount(long rejectedCount) { this.rejectedCount = rejectedCount; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
}
