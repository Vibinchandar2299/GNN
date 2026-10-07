package com.hiregraph.dto.response;

public class SkillDemandResponse {
    private String skillId;
    private String skillName;
    private long demandCount;
    private long supplyCount;
    private double demandRatio;

    public SkillDemandResponse() {}

    public SkillDemandResponse(String skillId, String skillName, long demandCount, long supplyCount, double demandRatio) {
        this.skillId = skillId;
        this.skillName = skillName;
        this.demandCount = demandCount;
        this.supplyCount = supplyCount;
        this.demandRatio = demandRatio;
    }

    public String getSkillId() { return skillId; }
    public void setSkillId(String skillId) { this.skillId = skillId; }

    public String getSkillName() { return skillName; }
    public void setSkillName(String skillName) { this.skillName = skillName; }

    public long getDemandCount() { return demandCount; }
    public void setDemandCount(long demandCount) { this.demandCount = demandCount; }

    public long getSupplyCount() { return supplyCount; }
    public void setSupplyCount(long supplyCount) { this.supplyCount = supplyCount; }

    public double getDemandRatio() { return demandRatio; }
    public void setDemandRatio(double demandRatio) { this.demandRatio = demandRatio; }
}
