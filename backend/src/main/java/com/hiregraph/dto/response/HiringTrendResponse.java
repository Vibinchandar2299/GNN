package com.hiregraph.dto.response;

public class HiringTrendResponse {
    private int cycle;
    private long totalApplications;
    private long selectedCount;
    private long rejectedCount;
    private double selectionRate;

    public HiringTrendResponse() {}

    public HiringTrendResponse(int cycle, long totalApplications, long selectedCount,
                               long rejectedCount, double selectionRate) {
        this.cycle = cycle;
        this.totalApplications = totalApplications;
        this.selectedCount = selectedCount;
        this.rejectedCount = rejectedCount;
        this.selectionRate = selectionRate;
    }

    public int getCycle() { return cycle; }
    public void setCycle(int cycle) { this.cycle = cycle; }

    public long getTotalApplications() { return totalApplications; }
    public void setTotalApplications(long totalApplications) { this.totalApplications = totalApplications; }

    public long getSelectedCount() { return selectedCount; }
    public void setSelectedCount(long selectedCount) { this.selectedCount = selectedCount; }

    public long getRejectedCount() { return rejectedCount; }
    public void setRejectedCount(long rejectedCount) { this.rejectedCount = rejectedCount; }

    public double getSelectionRate() { return selectionRate; }
    public void setSelectionRate(double selectionRate) { this.selectionRate = selectionRate; }
}
