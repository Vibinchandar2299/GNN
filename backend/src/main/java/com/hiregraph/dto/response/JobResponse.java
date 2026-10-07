package com.hiregraph.dto.response;

import java.util.List;

public class JobResponse {
    private String jobId;
    private String jobTitle;
    private String jobDomain;
    private Double minimumCgpa;
    private Integer experienceRequiredMonths;
    private Double salaryLpa;
    private Integer requiredSkillCount;
    private List<String> requiredSkills;

    public JobResponse() {}

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

    public List<String> getRequiredSkills() { return requiredSkills; }
    public void setRequiredSkills(List<String> requiredSkills) { this.requiredSkills = requiredSkills; }
}
