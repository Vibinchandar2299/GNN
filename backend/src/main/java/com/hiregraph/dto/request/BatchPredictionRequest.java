package com.hiregraph.dto.request;

import java.util.List;

public class BatchPredictionRequest {

    private List<String> applicationIds;
    private String modelName;
    private String modelVersion;
    private boolean forceRefresh;

    public BatchPredictionRequest() {}

    public BatchPredictionRequest(List<String> applicationIds) {
        this.applicationIds = applicationIds;
    }

    public List<String> getApplicationIds() {
        return applicationIds;
    }

    public void setApplicationIds(List<String> applicationIds) {
        this.applicationIds = applicationIds;
    }

    public String getModelName() {
        return modelName;
    }

    public void setModelName(String modelName) {
        this.modelName = modelName;
    }

    public String getModelVersion() {
        return modelVersion;
    }

    public void setModelVersion(String modelVersion) {
        this.modelVersion = modelVersion;
    }

    public boolean isForceRefresh() {
        return forceRefresh;
    }

    public void setForceRefresh(boolean forceRefresh) {
        this.forceRefresh = forceRefresh;
    }
}
