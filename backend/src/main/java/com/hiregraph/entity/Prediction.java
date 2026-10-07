package com.hiregraph.entity;

import jakarta.persistence.*;
import java.time.OffsetDateTime;

@Entity
@Table(name = "predictions", uniqueConstraints = {
    @UniqueConstraint(name = "uq_prediction_app_model", columnNames = {"application_id", "model_name", "model_version"})
})
public class Prediction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "application_id", nullable = false, length = 50)
    private String applicationId;

    @Column(name = "predicted_probability", nullable = false)
    private Double predictedProbability;

    @Column(name = "predicted_status", nullable = false, length = 20)
    private String predictedStatus;

    @Column(name = "model_name", nullable = false, length = 50)
    private String modelName;

    @Column(name = "model_version", nullable = false, length = 50)
    private String modelVersion;

    @Column(name = "created_at", nullable = false, updatable = false)
    private OffsetDateTime createdAt = OffsetDateTime.now();

    @Column(name = "updated_at", nullable = false)
    private OffsetDateTime updatedAt = OffsetDateTime.now();

    public Prediction() {}

    public Prediction(String applicationId, Double predictedProbability, String predictedStatus,
                      String modelName, String modelVersion) {
        this.applicationId = applicationId;
        this.predictedProbability = predictedProbability;
        this.predictedStatus = predictedStatus;
        this.modelName = modelName;
        this.modelVersion = modelVersion;
        this.createdAt = OffsetDateTime.now();
        this.updatedAt = OffsetDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getApplicationId() { return applicationId; }
    public void setApplicationId(String applicationId) { this.applicationId = applicationId; }

    public Double getPredictedProbability() { return predictedProbability; }
    public void setPredictedProbability(Double predictedProbability) { this.predictedProbability = predictedProbability; }

    public String getPredictedStatus() { return predictedStatus; }
    public void setPredictedStatus(String predictedStatus) { this.predictedStatus = predictedStatus; }

    public String getModelName() { return modelName; }
    public void setModelName(String modelName) { this.modelName = modelName; }

    public String getModelVersion() { return modelVersion; }
    public void setModelVersion(String modelVersion) { this.modelVersion = modelVersion; }

    public OffsetDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(OffsetDateTime createdAt) { this.createdAt = createdAt; }

    public OffsetDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(OffsetDateTime updatedAt) { this.updatedAt = updatedAt; }
}
