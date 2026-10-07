package com.hiregraph.dto.response;

import java.util.Map;

public class ModelMetadataResponse {
    private String projectName;
    private String researchTitle;
    private String modelName;
    private String checkpointFile;
    private String device;
    private Map<String, Object> verifiedResearchResults;
    private Map<String, Object> graphStatistics;
    private Map<String, Object> temporalSplit;
    private Map<String, Object> explainability;

    public ModelMetadataResponse() {}

    public String getProjectName() { return projectName; }
    public void setProjectName(String projectName) { this.projectName = projectName; }

    public String getResearchTitle() { return researchTitle; }
    public void setResearchTitle(String researchTitle) { this.researchTitle = researchTitle; }

    public String getModelName() { return modelName; }
    public void setModelName(String modelName) { this.modelName = modelName; }

    public String getCheckpointFile() { return checkpointFile; }
    public void setCheckpointFile(String checkpointFile) { this.checkpointFile = checkpointFile; }

    public String getDevice() { return device; }
    public void setDevice(String device) { this.device = device; }

    public Map<String, Object> getVerifiedResearchResults() { return verifiedResearchResults; }
    public void setVerifiedResearchResults(Map<String, Object> verifiedResearchResults) { this.verifiedResearchResults = verifiedResearchResults; }

    public Map<String, Object> getGraphStatistics() { return graphStatistics; }
    public void setGraphStatistics(Map<String, Object> graphStatistics) { this.graphStatistics = graphStatistics; }

    public Map<String, Object> getTemporalSplit() { return temporalSplit; }
    public void setTemporalSplit(Map<String, Object> temporalSplit) { this.temporalSplit = temporalSplit; }

    public Map<String, Object> getExplainability() { return explainability; }
    public void setExplainability(Map<String, Object> explainability) { this.explainability = explainability; }
}
