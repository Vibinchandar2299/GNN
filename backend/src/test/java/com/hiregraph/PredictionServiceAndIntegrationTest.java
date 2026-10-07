package com.hiregraph;

import com.hiregraph.client.AiServiceClient;
import com.hiregraph.dto.request.PredictionRequest;
import com.hiregraph.dto.response.PredictionResponse;
import com.hiregraph.entity.Prediction;
import com.hiregraph.exception.AiServiceException;
import com.hiregraph.exception.ResourceNotFoundException;
import com.hiregraph.repository.PredictionRepository;
import com.hiregraph.service.DataIngestionService;
import com.hiregraph.service.PredictionService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@SpringBootTest
public class PredictionServiceAndIntegrationTest {

    @Autowired
    private PredictionService predictionService;

    @Autowired
    private PredictionRepository predictionRepository;

    @Autowired
    private DataIngestionService ingestionService;

    @MockBean
    private AiServiceClient aiServiceClient;

    @BeforeEach
    void setup() {
        ingestionService.ingestData(false);

        // Clean up predictions for A00001 before test
        Optional<Prediction> existing = predictionRepository.findByApplicationIdAndModelNameAndModelVersion(
                "A00001", "AMRG-GraphSAGE", "research-v1"
        );
        existing.ifPresent(predictionRepository::delete);
    }

    @Test
    void testLivePredictionAndPersistence() {
        Map<String, Object> mockAiResult = new HashMap<>();
        mockAiResult.put("application_id", "A00001");
        mockAiResult.put("predicted_status", 1);
        mockAiResult.put("predicted_probability", 0.8063023686408997);
        mockAiResult.put("model_name", "AMRG-GraphSAGE");
        mockAiResult.put("model_version", "research-v1");

        when(aiServiceClient.predictApplication("A00001")).thenReturn(mockAiResult);

        PredictionRequest request = new PredictionRequest("AMRG-GraphSAGE", "research-v1", false);
        PredictionResponse response = predictionService.predictApplication("A00001", request);

        assertNotNull(response);
        assertEquals("A00001", response.getApplicationId());
        assertEquals("SELECTED", response.getPredictedStatus());
        assertEquals(0.8063023686408997, response.getEstimatedProbability(), 1e-6);

        // Verify persisted in PostgreSQL
        Optional<Prediction> persisted = predictionRepository.findByApplicationIdAndModelNameAndModelVersion(
                "A00001", "AMRG-GraphSAGE", "research-v1"
        );
        assertTrue(persisted.isPresent(), "Prediction must be persisted in PostgreSQL");
        assertEquals("SELECTED", persisted.get().getPredictedStatus());
        assertEquals(0.8063023686408997, persisted.get().getPredictedProbability(), 1e-6);

        // Verify AI service called once
        verify(aiServiceClient, times(1)).predictApplication("A00001");
    }

    @Test
    void testDuplicatePredictionPreventionAndCacheHit() {
        Map<String, Object> mockAiResult = new HashMap<>();
        mockAiResult.put("application_id", "A00001");
        mockAiResult.put("predicted_status", 1);
        mockAiResult.put("predicted_probability", 0.8063023686408997);

        when(aiServiceClient.predictApplication("A00001")).thenReturn(mockAiResult);

        PredictionRequest request = new PredictionRequest("AMRG-GraphSAGE", "research-v1", false);

        // First call: misses cache, calls AI service, persists
        PredictionResponse firstResponse = predictionService.predictApplication("A00001", request);
        assertNotNull(firstResponse);

        // Second call: hits PostgreSQL cache, does NOT call AI service
        PredictionResponse secondResponse = predictionService.predictApplication("A00001", request);
        assertNotNull(secondResponse);
        assertEquals(firstResponse.getEstimatedProbability(), secondResponse.getEstimatedProbability());
        assertEquals(firstResponse.getPredictedStatus(), secondResponse.getPredictedStatus());

        // AI service should only have been called ONCE
        verify(aiServiceClient, times(1)).predictApplication("A00001");

        // Verify exactly one prediction record exists in DB
        long count = predictionRepository.findAll().stream()
                .filter(p -> "A00001".equals(p.getApplicationId()) && "AMRG-GraphSAGE".equals(p.getModelName()))
                .count();
        assertEquals(1, count, "Must not create duplicate prediction rows in PostgreSQL");
    }

    @Test
    void testAiServiceFailureHandling() {
        when(aiServiceClient.predictApplication(anyString()))
                .thenThrow(new AiServiceException("Failed to connect to Python AI Service"));

        PredictionRequest request = new PredictionRequest("AMRG-GraphSAGE", "research-v1", false);
        assertThrows(AiServiceException.class, () -> {
            predictionService.predictApplication("A00001", request);
        });
    }

    @Test
    void testInvalidApplicationIdNotFound() {
        PredictionRequest request = new PredictionRequest("AMRG-GraphSAGE", "research-v1", false);
        assertThrows(ResourceNotFoundException.class, () -> {
            predictionService.predictApplication("NON_EXISTENT_APP_999", request);
        });
    }
}
