package com.hiregraph.repository;

import com.hiregraph.entity.Prediction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PredictionRepository extends JpaRepository<Prediction, Long> {
    Optional<Prediction> findByApplicationIdAndModelNameAndModelVersion(String applicationId, String modelName, String modelVersion);
    Optional<Prediction> findTopByApplicationIdOrderByCreatedAtDesc(String applicationId);
    boolean existsByApplicationIdAndModelNameAndModelVersion(String applicationId, String modelName, String modelVersion);
}
