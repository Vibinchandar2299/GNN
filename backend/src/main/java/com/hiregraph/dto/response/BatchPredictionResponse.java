package com.hiregraph.dto.response;

import java.util.List;

public class BatchPredictionResponse {

    private int totalRequested;
    private int totalPredicted;
    private List<PredictionResponse> predictions;

    public BatchPredictionResponse() {}

    public BatchPredictionResponse(int totalRequested, int totalPredicted, List<PredictionResponse> predictions) {
        this.totalRequested = totalRequested;
        this.totalPredicted = totalPredicted;
        this.predictions = predictions;
    }

    public int getTotalRequested() {
        return totalRequested;
    }

    public void setTotalRequested(int totalRequested) {
        this.totalRequested = totalRequested;
    }

    public int getTotalPredicted() {
        return totalPredicted;
    }

    public void setTotalPredicted(int totalPredicted) {
        this.totalPredicted = totalPredicted;
    }

    public List<PredictionResponse> getPredictions() {
        return predictions;
    }

    public void setPredictions(List<PredictionResponse> predictions) {
        this.predictions = predictions;
    }
}
