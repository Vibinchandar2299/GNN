package com.hiregraph.entity;

import jakarta.persistence.*;
import java.time.OffsetDateTime;

@Entity
@Table(name = "companies")
public class Company {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "company_id", unique = true, nullable = false, length = 50)
    private String companyId;

    @Column(name = "company_name", length = 150)
    private String companyName;

    @Column(name = "industry", nullable = false, length = 100)
    private String industry;

    @Column(name = "company_size", nullable = false, length = 50)
    private String companySize;

    @Column(name = "historical_selection_rate", nullable = false)
    private Double historicalSelectionRate;

    @Column(name = "historical_average_selected_cgpa", nullable = false)
    private Double historicalAverageSelectedCgpa;

    @Column(name = "created_at", nullable = false, updatable = false)
    private OffsetDateTime createdAt = OffsetDateTime.now();

    @Column(name = "updated_at", nullable = false)
    private OffsetDateTime updatedAt = OffsetDateTime.now();

    public Company() {}

    public Company(String companyId, String companyName, String industry, String companySize,
                   Double historicalSelectionRate, Double historicalAverageSelectedCgpa) {
        this.companyId = companyId;
        this.companyName = companyName;
        this.industry = industry;
        this.companySize = companySize;
        this.historicalSelectionRate = historicalSelectionRate;
        this.historicalAverageSelectedCgpa = historicalAverageSelectedCgpa;
        this.createdAt = OffsetDateTime.now();
        this.updatedAt = OffsetDateTime.now();
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

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

    public OffsetDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(OffsetDateTime createdAt) { this.createdAt = createdAt; }

    public OffsetDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(OffsetDateTime updatedAt) { this.updatedAt = updatedAt; }
}
