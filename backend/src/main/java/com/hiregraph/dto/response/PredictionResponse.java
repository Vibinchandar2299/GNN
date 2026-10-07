package com.hiregraph.dto.response;

public class PredictionResponse {
    private String applicationId;
    private String predictedStatus;
    private Double estimatedProbability;
    private String modelName;
    private String modelVersion;
    private String decisionSupportLabel;
    private String disclaimer;

    public PredictionResponse() {}

    public PredictionResponse(String applicationId, String predictedStatus, Double estimatedProbability,
                              String modelName, String modelVersion, String decisionSupportLabel, String disclaimer) {
        this.applicationId = applicationId;
        this.predictedStatus = predictedStatus;
        this.estimatedProbability = estimatedProbability;
        this.modelName = modelName;
        this.modelVersion = modelVersion;
        this.decisionSupportLabel = decisionSupportLabel;
        this.disclaimer = disclaimer;
    }

    public String getApplicationId() { return applicationId; }
    public void setApplicationId(String applicationId) { this.applicationId = applicationId; }

    public String getPredictedStatus() { return predictedStatus; }
    public void setPredictedStatus(String predictedStatus) { this.predictedStatus = predictedStatus; }

    public Double getEstimatedProbability() { return estimatedProbability; }
    public void setEstimatedProbability(Double estimatedProbability) { this.estimatedProbability = estimatedProbability; }

    public String getModelName() { return modelName; }
    public void setModelName(String modelName) { this.modelName = modelName; }

    public String getModelVersion() { return modelVersion; }
    public void setModelVersion(String modelVersion) { this.modelVersion = modelVersion; }

    public String getDecisionSupportLabel() { return decisionSupportLabel; }
    public void setDecisionSupportLabel(String decisionSupportLabel) { this.decisionSupportLabel = decisionSupportLabel; }

    public String getDisclaimer() { return disclaimer; }
    public void setDisclaimer(String disclaimer) { this.disclaimer = disclaimer; }
}
