package com.hiregraph.entity;

import jakarta.persistence.*;
import java.time.OffsetDateTime;

@Entity
@Table(name = "model_benchmarks")
public class ModelBenchmark {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "model_name", unique = true, nullable = false, length = 100)
    private String modelName;

    @Column(name = "accuracy", nullable = false)
    private Double accuracy;

    @Column(name = "precision_score", nullable = false)
    private Double precisionScore;

    @Column(name = "recall", nullable = false)
    private Double recall;

    @Column(name = "f1_score", nullable = false)
    private Double f1Score;

    @Column(name = "roc_auc", nullable = false)
    private Double rocAuc;

    @Column(name = "dataset_description", length = 255)
    private String datasetDescription;

    @Column(name = "created_at", nullable = false, updatable = false)
    private OffsetDateTime createdAt = OffsetDateTime.now();

    public ModelBenchmark() {}

    public ModelBenchmark(String modelName, Double accuracy, Double precisionScore, Double recall,
                          Double f1Score, Double rocAuc, String datasetDescription) {
        this.modelName = modelName;
        this.accuracy = accuracy;
        this.precisionScore = precisionScore;
        this.recall = recall;
        this.f1Score = f1Score;
        this.rocAuc = rocAuc;
        this.datasetDescription = datasetDescription;
        this.createdAt = OffsetDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

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

    public OffsetDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(OffsetDateTime createdAt) { this.createdAt = createdAt; }
}
