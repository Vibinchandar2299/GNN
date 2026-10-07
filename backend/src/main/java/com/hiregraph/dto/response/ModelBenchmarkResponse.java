package com.hiregraph.dto.response;

public class ModelBenchmarkResponse {
    private String modelName;
    private Double accuracy;
    private Double precisionScore;
    private Double recall;
    private Double f1Score;
    private Double rocAuc;
    private String datasetDescription;

    public ModelBenchmarkResponse() {}

    public ModelBenchmarkResponse(String modelName, Double accuracy, Double precisionScore,
                                  Double recall, Double f1Score, Double rocAuc, String datasetDescription) {
        this.modelName = modelName;
        this.accuracy = accuracy;
        this.precisionScore = precisionScore;
        this.recall = recall;
        this.f1Score = f1Score;
        this.rocAuc = rocAuc;
        this.datasetDescription = datasetDescription;
    }

    public String getModelName() { return modelName; }
    public void setModelName(String modelName) { this.modelName = modelName; }

    public Double getAccuracy() { return accuracy; }
    public void setAccuracy(Double accuracy) { this.accuracy = accuracy; }

    public Double getPrecisionScore() { return precisionScore; }
    public void setPrecisionScore(Double precisionScore) { this.precisionScore = precisionScore; }

    public Double getRecall() { return recall; }
    public void setRecall(Double recall) { this.recall = recall; }

    public Double getF1Score() { return f1Score; }
    public void setF1Score(Double f1Score) { this.f1Score = f1Score; }

    public Double getRocAuc() { return rocAuc; }
    public void setRocAuc(Double rocAuc) { this.rocAuc = rocAuc; }

    public String getDatasetDescription() { return datasetDescription; }
    public void setDatasetDescription(String datasetDescription) { this.datasetDescription = datasetDescription; }
}
