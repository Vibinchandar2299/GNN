package com.hiregraph.dto.response;

public class DashboardSummaryResponse {
    private long totalApplications;
    private long totalStudents;
    private long totalCompanies;
    private long totalJobs;
    private long totalSkills;
    private long selectedCount;
    private long rejectedCount;
    private double selectionRate;

    public DashboardSummaryResponse() {}

    public DashboardSummaryResponse(long totalApplications, long totalStudents, long totalCompanies,
                                    long totalJobs, long totalSkills, long selectedCount,
                                    long rejectedCount, double selectionRate) {
        this.totalApplications = totalApplications;
        this.totalStudents = totalStudents;
        this.totalCompanies = totalCompanies;
        this.totalJobs = totalJobs;
        this.totalSkills = totalSkills;
        this.selectedCount = selectedCount;
        this.rejectedCount = rejectedCount;
        this.selectionRate = selectionRate;
    }

    public long getTotalApplications() { return totalApplications; }
    public void setTotalApplications(long totalApplications) { this.totalApplications = totalApplications; }

    public long getTotalStudents() { return totalStudents; }
    public void setTotalStudents(long totalStudents) { this.totalStudents = totalStudents; }

    public long getTotalCompanies() { return totalCompanies; }
    public void setTotalCompanies(long totalCompanies) { this.totalCompanies = totalCompanies; }

    public long getTotalJobs() { return totalJobs; }
    public void setTotalJobs(long totalJobs) { this.totalJobs = totalJobs; }

    public long getTotalSkills() { return totalSkills; }
    public void setTotalSkills(long totalSkills) { this.totalSkills = totalSkills; }

    public long getSelectedCount() { return selectedCount; }
    public void setSelectedCount(long selectedCount) { this.selectedCount = selectedCount; }

    public long getRejectedCount() { return rejectedCount; }
    public void setRejectedCount(long rejectedCount) { this.rejectedCount = rejectedCount; }

    public double getSelectionRate() { return selectionRate; }
    public void setSelectionRate(double selectionRate) { this.selectionRate = selectionRate; }
}
