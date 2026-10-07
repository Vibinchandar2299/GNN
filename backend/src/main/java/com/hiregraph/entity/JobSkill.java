package com.hiregraph.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "job_skills", uniqueConstraints = {
    @UniqueConstraint(name = "uq_job_skill", columnNames = {"job_id", "skill_id"})
})
public class JobSkill {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "job_id", nullable = false, length = 50)
    private String jobId;

    @Column(name = "skill_id", nullable = false, length = 50)
    private String skillId;

    @Column(name = "required_skill_level")
    private Double requiredSkillLevel;

    public JobSkill() {}

    public JobSkill(String jobId, String skillId, Double requiredSkillLevel) {
        this.jobId = jobId;
        this.skillId = skillId;
        this.requiredSkillLevel = requiredSkillLevel;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getJobId() { return jobId; }
    public void setJobId(String jobId) { this.jobId = jobId; }

    public String getSkillId() { return skillId; }
    public void setSkillId(String skillId) { this.skillId = skillId; }

    public Double getRequiredSkillLevel() { return requiredSkillLevel; }
    public void setRequiredSkillLevel(Double requiredSkillLevel) { this.requiredSkillLevel = requiredSkillLevel; }
}
