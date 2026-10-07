package com.hiregraph.dto.response;

public class SkillResponse {
    private String skillId;
    private String skillName;
    private long studentCount;
    private long jobCount;

    public SkillResponse() {}

    public SkillResponse(String skillId, String skillName, long studentCount, long jobCount) {
        this.skillId = skillId;
        this.skillName = skillName;
        this.studentCount = studentCount;
        this.jobCount = jobCount;
    }

    public String getSkillId() { return skillId; }
    public void setSkillId(String skillId) { this.skillId = skillId; }

    public String getSkillName() { return skillName; }
    public void setSkillName(String skillName) { this.skillName = skillName; }

    public long getStudentCount() { return studentCount; }
    public void setStudentCount(long studentCount) { this.studentCount = studentCount; }

    public long getJobCount() { return jobCount; }
    public void setJobCount(long jobCount) { this.jobCount = jobCount; }
}
