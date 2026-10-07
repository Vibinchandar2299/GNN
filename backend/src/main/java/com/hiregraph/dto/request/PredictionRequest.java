package com.hiregraph.dto.request;

public class PredictionRequest {
    private String modelName = "AMRG-GraphSAGE";
    private String modelVersion = "research-v1";
    private boolean forceRefresh = false;

    public PredictionRequest() {}

    public PredictionRequest(String modelName, String modelVersion, boolean forceRefresh) {
        this.modelName = modelName;
        this.modelVersion = modelVersion;
        this.forceRefresh = forceRefresh;
    }

    public String getModelName() { return modelName; }
    public void setModelName(String modelName) { this.modelName = modelName; }

    public String getModelVersion() { return modelVersion; }
    public void setModelVersion(String modelVersion) { this.modelVersion = modelVersion; }

    public boolean isForceRefresh() { return forceRefresh; }
    public void setForceRefresh(boolean forceRefresh) { this.forceRefresh = forceRefresh; }
}
