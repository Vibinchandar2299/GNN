package com.hiregraph.dto.response;

public class CompanyResponse {
    private String companyId;
    private String companyName;
    private String industry;
    private String companySize;
    private Double historicalSelectionRate;
    private Double historicalAverageSelectedCgpa;
    private long totalApplications;

    public CompanyResponse() {}

    public String getCompanyId() { return companyId; }
    public void setCompanyId(String companyId) { this.companyId = companyId; }

    public String getCompanyName() { return companyName; }
    public void setCompanyName(String companyName) { this.companyName = companyName; }

    public String getIndustry() { return industry; }
    public void setIndustry(String industry) { this.industry = industry; }

    public String getCompanySize() { return companySize; }
    public void setCompanySize(String companySize) { this.companySize = companySize; }

    public Double getHistoricalSelectionRate() { return historicalSelectionRate; }
    public void setHistoricalSelectionRate(Double historicalSelectionRate) { this.historicalSelectionRate = historicalSelectionRate; }

    public Double getHistoricalAverageSelectedCgpa() { return historicalAverageSelectedCgpa; }
    public void setHistoricalAverageSelectedCgpa(Double historicalAverageSelectedCgpa) { this.historicalAverageSelectedCgpa = historicalAverageSelectedCgpa; }

    public long getTotalApplications() { return totalApplications; }
    public void setTotalApplications(long totalApplications) { this.totalApplications = totalApplications; }
}
