package com.hiregraph.entity;

import jakarta.persistence.*;
import java.time.OffsetDateTime;

@Entity
@Table(name = "applications")
public class Application {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "application_id", unique = true, nullable = false, length = 50)
    private String applicationId;

    @Column(name = "student_id", nullable = false, length = 50)
    private String studentId;

    @Column(name = "company_id", nullable = false, length = 50)
    private String companyId;

    @Column(name = "job_id", nullable = false, length = 50)
    private String jobId;

    @Column(name = "cycle", nullable = false)
    private Integer cycle;

    @Column(name = "relevant_experience_months", nullable = false)
    private Double relevantExperienceMonths;

    @Column(name = "total_skill_count", nullable = false)
    private Integer totalSkillCount;

    @Column(name = "average_skill_proficiency", nullable = false)
    private Double averageSkillProficiency;

    @Column(name = "role_shift_score", nullable = false)
    private Double roleShiftScore;

    @Column(name = "skill_match_ratio", nullable = false)
    private Double skillMatchRatio;

    @Column(name = "required_skill_level_gap", nullable = false)
    private Double requiredSkillLevelGap;

    @Column(name = "role_experience_match", nullable = false)
    private Double roleExperienceMatch;

    @Column(name = "expected_hiring_count", nullable = false)
    private Integer expectedHiringCount;

    @Column(name = "final_status", nullable = false)
    private Integer finalStatus;

    @Column(name = "created_at", nullable = false, updatable = false)
    private OffsetDateTime createdAt = OffsetDateTime.now();

    @Column(name = "updated_at", nullable = false)
    private OffsetDateTime updatedAt = OffsetDateTime.now();

    public Application() {}

    public Application(String applicationId, String studentId, String companyId, String jobId,
                       Integer cycle, Double relevantExperienceMonths, Integer totalSkillCount,
                       Double averageSkillProficiency, Double roleShiftScore, Double skillMatchRatio,
                       Double requiredSkillLevelGap, Double roleExperienceMatch,
                       Integer expectedHiringCount, Integer finalStatus) {
        this.applicationId = applicationId;
        this.studentId = studentId;
        this.companyId = companyId;
        this.jobId = jobId;
        this.cycle = cycle;
        this.relevantExperienceMonths = relevantExperienceMonths;
        this.totalSkillCount = totalSkillCount;
        this.averageSkillProficiency = averageSkillProficiency;
        this.roleShiftScore = roleShiftScore;
        this.skillMatchRatio = skillMatchRatio;
        this.requiredSkillLevelGap = requiredSkillLevelGap;
        this.roleExperienceMatch = roleExperienceMatch;
        this.expectedHiringCount = expectedHiringCount;
        this.finalStatus = finalStatus;
        this.createdAt = OffsetDateTime.now();
        this.updatedAt = OffsetDateTime.now();
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getApplicationId() { return applicationId; }
    public void setApplicationId(String applicationId) { this.applicationId = applicationId; }

    public String getStudentId() { return studentId; }
    public void setStudentId(String studentId) { this.studentId = studentId; }

    public String getCompanyId() { return companyId; }
    public void setCompanyId(String companyId) { this.companyId = companyId; }

    public String getJobId() { return jobId; }
    public void setJobId(String jobId) { this.jobId = jobId; }

    public Integer getCycle() { return cycle; }
    public void setCycle(Integer cycle) { this.cycle = cycle; }

    public Double getRelevantExperienceMonths() { return relevantExperienceMonths; }
    public void setRelevantExperienceMonths(Double relevantExperienceMonths) { this.relevantExperienceMonths = relevantExperienceMonths; }

    public Integer getTotalSkillCount() { return totalSkillCount; }
    public void setTotalSkillCount(Integer totalSkillCount) { this.totalSkillCount = totalSkillCount; }

    public Double getAverageSkillProficiency() { return averageSkillProficiency; }
    public void setAverageSkillProficiency(Double averageSkillProficiency) { this.averageSkillProficiency = averageSkillProficiency; }

    public Double getRoleShiftScore() { return roleShiftScore; }
    public void setRoleShiftScore(Double roleShiftScore) { this.roleShiftScore = roleShiftScore; }

    public Double getSkillMatchRatio() { return skillMatchRatio; }
    public void setSkillMatchRatio(Double skillMatchRatio) { this.skillMatchRatio = skillMatchRatio; }

    public Double getRequiredSkillLevelGap() { return requiredSkillLevelGap; }
    public void setRequiredSkillLevelGap(Double requiredSkillLevelGap) { this.requiredSkillLevelGap = requiredSkillLevelGap; }

    public Double getRoleExperienceMatch() { return roleExperienceMatch; }
    public void setRoleExperienceMatch(Double roleExperienceMatch) { this.roleExperienceMatch = roleExperienceMatch; }

    public Integer getExpectedHiringCount() { return expectedHiringCount; }
    public void setExpectedHiringCount(Integer expectedHiringCount) { this.expectedHiringCount = expectedHiringCount; }

    public Integer getFinalStatus() { return finalStatus; }
    public void setFinalStatus(Integer finalStatus) { this.finalStatus = finalStatus; }

    public OffsetDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(OffsetDateTime createdAt) { this.createdAt = createdAt; }

    public OffsetDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(OffsetDateTime updatedAt) { this.updatedAt = updatedAt; }
}
