package com.hiregraph.entity;

import jakarta.persistence.*;
import java.time.OffsetDateTime;

@Entity
@Table(name = "students")
public class Student {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "student_id", unique = true, nullable = false, length = 50)
    private String studentId;

    @Column(name = "department", nullable = false, length = 100)
    private String department;

    @Column(name = "cgpa", nullable = false)
    private Double cgpa;

    @Column(name = "backlogs", nullable = false)
    private Integer backlogs;

    @Column(name = "aptitude_score_pre", nullable = false)
    private Double aptitudeScorePre;

    @Column(name = "coding_score_pre", nullable = false)
    private Double codingScorePre;

    @Column(name = "communication_score_pre", nullable = false)
    private Double communicationScorePre;

    @Column(name = "projects_count", nullable = false)
    private Integer projectsCount;

    @Column(name = "internships_count", nullable = false)
    private Integer internshipsCount;

    @Column(name = "certifications_count", nullable = false)
    private Integer certificationsCount;

    @Column(name = "resume_score", nullable = false)
    private Double resumeScore;

    @Column(name = "created_at", nullable = false, updatable = false)
    private OffsetDateTime createdAt = OffsetDateTime.now();

    @Column(name = "updated_at", nullable = false)
    private OffsetDateTime updatedAt = OffsetDateTime.now();

    public Student() {}

    public Student(String studentId, String department, Double cgpa, Integer backlogs,
                   Double aptitudeScorePre, Double codingScorePre, Double communicationScorePre,
                   Integer projectsCount, Integer internshipsCount, Integer certificationsCount,
                   Double resumeScore) {
        this.studentId = studentId;
        this.department = department;
        this.cgpa = cgpa;
        this.backlogs = backlogs;
        this.aptitudeScorePre = aptitudeScorePre;
        this.codingScorePre = codingScorePre;
        this.communicationScorePre = communicationScorePre;
        this.projectsCount = projectsCount;
        this.internshipsCount = internshipsCount;
        this.certificationsCount = certificationsCount;
        this.resumeScore = resumeScore;
        this.createdAt = OffsetDateTime.now();
        this.updatedAt = OffsetDateTime.now();
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getStudentId() { return studentId; }
    public void setStudentId(String studentId) { this.studentId = studentId; }

    public String getDepartment() { return department; }
    public void setDepartment(String department) { this.department = department; }

    public Double getCgpa() { return cgpa; }
    public void setCgpa(Double cgpa) { this.cgpa = cgpa; }

    public Integer getBacklogs() { return backlogs; }
    public void setBacklogs(Integer backlogs) { this.backlogs = backlogs; }

    public Double getAptitudeScorePre() { return aptitudeScorePre; }
    public void setAptitudeScorePre(Double aptitudeScorePre) { this.aptitudeScorePre = aptitudeScorePre; }

    public Double getCodingScorePre() { return codingScorePre; }
    public void setCodingScorePre(Double codingScorePre) { this.codingScorePre = codingScorePre; }

    public Double getCommunicationScorePre() { return communicationScorePre; }
    public void setCommunicationScorePre(Double communicationScorePre) { this.communicationScorePre = communicationScorePre; }

    public Integer getProjectsCount() { return projectsCount; }
    public void setProjectsCount(Integer projectsCount) { this.projectsCount = projectsCount; }

    public Integer getInternshipsCount() { return internshipsCount; }
    public void setInternshipsCount(Integer internshipsCount) { this.internshipsCount = internshipsCount; }

    public Integer getCertificationsCount() { return certificationsCount; }
    public void setCertificationsCount(Integer certificationsCount) { this.certificationsCount = certificationsCount; }

    public Double getResumeScore() { return resumeScore; }
    public void setResumeScore(Double resumeScore) { this.resumeScore = resumeScore; }

    public OffsetDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(OffsetDateTime createdAt) { this.createdAt = createdAt; }

    public OffsetDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(OffsetDateTime updatedAt) { this.updatedAt = updatedAt; }
}
