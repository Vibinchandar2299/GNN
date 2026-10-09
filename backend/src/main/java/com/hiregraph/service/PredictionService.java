package com.hiregraph.service;

import com.hiregraph.client.AiServiceClient;
import com.hiregraph.dto.request.PredictionRequest;
import com.hiregraph.dto.response.PredictionResponse;
import com.hiregraph.entity.Application;
import com.hiregraph.entity.Prediction;
import com.hiregraph.enums.PredictedStatus;
import com.hiregraph.exception.ResourceNotFoundException;
import com.hiregraph.mapper.EntityDtoMapper;
import com.hiregraph.repository.ApplicationRepository;
import com.hiregraph.repository.PredictionRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.OffsetDateTime;
import java.util.Map;
import java.util.Optional;

@Service
public class PredictionService {

    private static final Logger log = LoggerFactory.getLogger(PredictionService.class);
    private static final String DEFAULT_MODEL = "AMRG-GraphSAGE";
    private static final String DEFAULT_VERSION = "research-v1";

    private final ApplicationRepository applicationRepository;
    private final PredictionRepository predictionRepository;
    private final AiServiceClient aiServiceClient;

    public PredictionService(ApplicationRepository applicationRepository,
                             PredictionRepository predictionRepository,
                             AiServiceClient aiServiceClient) {
        this.applicationRepository = applicationRepository;
        this.predictionRepository = predictionRepository;
        this.aiServiceClient = aiServiceClient;
    }

    @Transactional
    public PredictionResponse predictApplication(String applicationId) {
        return predictApplication(applicationId, null);
    }

    @Transactional
    public PredictionResponse predictApplication(String applicationId, PredictionRequest request) {
        String cleanAppId = applicationId.trim();
        String modelName = (request != null && request.getModelName() != null) ? request.getModelName() : DEFAULT_MODEL;
        String modelVersion = (request != null && request.getModelVersion() != null) ? request.getModelVersion() : DEFAULT_VERSION;
        boolean forceRefresh = request != null && request.isForceRefresh();

        // 1. Verify application exists in DB
        Application application = applicationRepository.findByApplicationId(cleanAppId)
                .orElseThrow(() -> new ResourceNotFoundException("Application with ID '" + cleanAppId + "' not found."));

        // 2. Check prediction cache in PostgreSQL
        Optional<Prediction> existingOpt = predictionRepository.findByApplicationIdAndModelNameAndModelVersion(
                cleanAppId, modelName, modelVersion
        );

        if (existingOpt.isPresent() && !forceRefresh) {
            log.info("Returning cached prediction for application {} (model: {}, version: {})", cleanAppId, modelName, modelVersion);
            return EntityDtoMapper.toPredictionResponse(existingOpt.get());
        }

        // 3. Delegate inference to Python FastAPI AI service
        log.info("Requesting live inference from FastAPI for application {}", cleanAppId);
        Map<String, Object> aiResult = aiServiceClient.predictApplication(cleanAppId);

        Number probNum = (Number) aiResult.get("predicted_probability");
        Number statusNum = (Number) aiResult.get("predicted_status");
        double probability = probNum != null ? probNum.doubleValue() : 0.0;
        int statusInt = statusNum != null ? statusNum.intValue() : 0;
        String statusStr = PredictedStatus.fromInt(statusInt).name();

        // 4. Save or update prediction record (duplicate-safe)
        Prediction prediction;
        if (existingOpt.isPresent()) {
            prediction = existingOpt.get();
            prediction.setPredictedProbability(probability);
            prediction.setPredictedStatus(statusStr);
            prediction.setUpdatedAt(OffsetDateTime.now());
        } else {
            prediction = new Prediction(cleanAppId, probability, statusStr, modelName, modelVersion);
        }

        Prediction saved = predictionRepository.save(prediction);
        log.info("Persisted prediction for application {}: status={}, prob={}", cleanAppId, statusStr, probability);

        return EntityDtoMapper.toPredictionResponse(saved);
    }

    @Transactional
    public com.hiregraph.dto.response.BatchPredictionResponse predictBatch(com.hiregraph.dto.request.BatchPredictionRequest request) {
        if (request == null || request.getApplicationIds() == null || request.getApplicationIds().isEmpty()) {
            return new com.hiregraph.dto.response.BatchPredictionResponse(0, 0, java.util.Collections.emptyList());
        }

        List<String> appIds = request.getApplicationIds().stream()
                .map(String::trim)
                .distinct()
                .toList();

        String modelName = request.getModelName() != null ? request.getModelName() : DEFAULT_MODEL;
        String modelVersion = request.getModelVersion() != null ? request.getModelVersion() : DEFAULT_VERSION;
        boolean forceRefresh = request.isForceRefresh();

        List<PredictionResponse> results = new java.util.ArrayList<>();
        List<String> needInference = new java.util.ArrayList<>();

        if (!forceRefresh) {
            for (String appId : appIds) {
                Optional<Prediction> cached = predictionRepository.findByApplicationIdAndModelNameAndModelVersion(
                        appId, modelName, modelVersion
                );
                if (cached.isPresent()) {
                    results.add(EntityDtoMapper.toPredictionResponse(cached.get()));
                } else {
                    needInference.add(appId);
                }
            }
        } else {
            needInference.addAll(appIds);
        }

        if (!needInference.isEmpty()) {
            Map<String, Object> aiBatchResult = aiServiceClient.predictBatch(needInference);
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> predictionsList = (List<Map<String, Object>>) aiBatchResult.get("predictions");

            if (predictionsList != null) {
                for (Map<String, Object> item : predictionsList) {
                    String appId = (String) item.get("application_id");
                    Number probNum = (Number) item.get("predicted_probability");
                    Number statusNum = (Number) item.get("predicted_status");
                    double probability = probNum != null ? probNum.doubleValue() : 0.0;
                    int statusInt = statusNum != null ? statusNum.intValue() : 0;
                    String statusStr = PredictedStatus.fromInt(statusInt).name();

                    Optional<Prediction> existingOpt = predictionRepository.findByApplicationIdAndModelNameAndModelVersion(
                            appId, modelName, modelVersion
                    );
                    Prediction prediction;
                    if (existingOpt.isPresent()) {
                        prediction = existingOpt.get();
                        prediction.setPredictedProbability(probability);
                        prediction.setPredictedStatus(statusStr);
                        prediction.setUpdatedAt(OffsetDateTime.now());
                    } else {
                        prediction = new Prediction(appId, probability, statusStr, modelName, modelVersion);
                    }
                    Prediction saved = predictionRepository.save(prediction);
                    results.add(EntityDtoMapper.toPredictionResponse(saved));
                }
            }
        }

        return new com.hiregraph.dto.response.BatchPredictionResponse(appIds.size(), results.size(), results);
    }
}
