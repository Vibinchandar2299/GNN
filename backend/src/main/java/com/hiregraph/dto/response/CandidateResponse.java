package com.hiregraph.dto.response;

import java.util.List;

public class CandidateResponse {
    private String studentId;
    private String department;
    private Double cgpa;
    private Integer backlogs;
    private Double aptitudeScorePre;
    private Double codingScorePre;
    private Double communicationScorePre;
    private Integer projectsCount;
    private Integer internshipsCount;
    private Integer certificationsCount;
    private Double resumeScore;
    private List<String> skills;

    public CandidateResponse() {}

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

    public List<String> getSkills() { return skills; }
    public void setSkills(List<String> skills) { this.skills = skills; }
}
