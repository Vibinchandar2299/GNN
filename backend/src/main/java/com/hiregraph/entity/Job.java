package com.hiregraph.entity;

import jakarta.persistence.*;
import java.time.OffsetDateTime;

@Entity
@Table(name = "jobs")
public class Job {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "job_id", unique = true, nullable = false, length = 50)
    private String jobId;

    @Column(name = "job_title", nullable = false, length = 150)
    private String jobTitle;

    @Column(name = "job_domain", nullable = false, length = 100)
    private String jobDomain;

    @Column(name = "minimum_cgpa", nullable = false)
    private Double minimumCgpa;

    @Column(name = "experience_required_months", nullable = false)
    private Integer experienceRequiredMonths;

    @Column(name = "salary_lpa", nullable = false)
    private Double salaryLpa;

    @Column(name = "required_skill_count", nullable = false)
    private Integer requiredSkillCount;

    @Column(name = "created_at", nullable = false, updatable = false)
    private OffsetDateTime createdAt = OffsetDateTime.now();

    @Column(name = "updated_at", nullable = false)
    private OffsetDateTime updatedAt = OffsetDateTime.now();

    public Job() {}

    public Job(String jobId, String jobTitle, String jobDomain, Double minimumCgpa,
               Integer experienceRequiredMonths, Double salaryLpa, Integer requiredSkillCount) {
        this.jobId = jobId;
        this.jobTitle = jobTitle;
        this.jobDomain = jobDomain;
        this.minimumCgpa = minimumCgpa;
        this.experienceRequiredMonths = experienceRequiredMonths;
        this.salaryLpa = salaryLpa;
        this.requiredSkillCount = requiredSkillCount;
        this.createdAt = OffsetDateTime.now();
        this.updatedAt = OffsetDateTime.now();
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getJobId() { return jobId; }
    public void setJobId(String jobId) { this.jobId = jobId; }

    public String getJobTitle() { return jobTitle; }
    public void setJobTitle(String jobTitle) { this.jobTitle = jobTitle; }

    public String getJobDomain() { return jobDomain; }
    public void setJobDomain(String jobDomain) { this.jobDomain = jobDomain; }

    public Double getMinimumCgpa() { return minimumCgpa; }
    public void setMinimumCgpa(Double minimumCgpa) { this.minimumCgpa = minimumCgpa; }

    public Integer getExperienceRequiredMonths() { return experienceRequiredMonths; }
    public void setExperienceRequiredMonths(Integer experienceRequiredMonths) { this.experienceRequiredMonths = experienceRequiredMonths; }

    public Double getSalaryLpa() { return salaryLpa; }
    public void setSalaryLpa(Double salaryLpa) { this.salaryLpa = salaryLpa; }

    public Integer getRequiredSkillCount() { return requiredSkillCount; }
    public void setRequiredSkillCount(Integer requiredSkillCount) { this.requiredSkillCount = requiredSkillCount; }

    public OffsetDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(OffsetDateTime createdAt) { this.createdAt = createdAt; }

    public OffsetDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(OffsetDateTime updatedAt) { this.updatedAt = updatedAt; }
}
