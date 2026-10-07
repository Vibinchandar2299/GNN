package com.hiregraph.dto.response;

public class ApplicationResponse {
    private String applicationId;
    private String studentId;
    private String companyId;
    private String jobId;
    private Integer cycle;
    private Double relevantExperienceMonths;
    private Integer totalSkillCount;
    private Double averageSkillProficiency;
    private Double roleShiftScore;
    private Double skillMatchRatio;
    private Double requiredSkillLevelGap;
    private Double roleExperienceMatch;
    private Integer expectedHiringCount;
    private Integer finalStatus;
    private String finalStatusLabel;
    private PredictionResponse latestPrediction;

    public ApplicationResponse() {}

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
    public void setFinalStatus(Integer finalStatus) {
        this.finalStatus = finalStatus;
        this.finalStatusLabel = (finalStatus != null && finalStatus == 1) ? "Selected" : "Rejected";
    }

    public String getFinalStatusLabel() { return finalStatusLabel; }
    public void setFinalStatusLabel(String finalStatusLabel) { this.finalStatusLabel = finalStatusLabel; }

    public PredictionResponse getLatestPrediction() { return latestPrediction; }
    public void setLatestPrediction(PredictionResponse latestPrediction) { this.latestPrediction = latestPrediction; }
}
