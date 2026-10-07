package com.hiregraph.client;

import com.hiregraph.exception.AiServiceException;
import com.hiregraph.exception.ResourceNotFoundException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpStatusCode;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientRequestException;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import java.util.Collections;
import java.util.List;
import java.util.Map;

@Component
public class AiServiceClient {

    private static final Logger log = LoggerFactory.getLogger(AiServiceClient.class);
    private final WebClient webClient;

    public AiServiceClient(WebClient aiServiceWebClient) {
        this.webClient = aiServiceWebClient;
    }

    public Map<String, Object> getHealth() {
        try {
            return webClient.get()
                    .uri("/health")
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, response ->
                            response.bodyToMono(String.class).map(msg -> new AiServiceException("AI Health check failed: " + msg)))
                    .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                    .block();
        } catch (WebClientRequestException ex) {
            log.error("Failed to connect to AI service health endpoint: {}", ex.getMessage());
            throw new AiServiceException("Failed to connect to Python AI Service: " + ex.getMessage(), ex);
        }
    }

    public Map<String, Object> getModelMetadata() {
        try {
            return webClient.get()
                    .uri("/model/metadata")
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, response ->
                            response.bodyToMono(String.class).map(msg -> new AiServiceException("AI Model metadata failed: " + msg)))
                    .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                    .block();
        } catch (WebClientRequestException ex) {
            log.error("Failed to connect to AI service metadata endpoint: {}", ex.getMessage());
            throw new AiServiceException("Failed to connect to Python AI Service: " + ex.getMessage(), ex);
        }
    }

    public Map<String, Object> predictApplication(String applicationId) {
        try {
            return webClient.post()
                    .uri("/predict/application/{id}", applicationId)
                    .retrieve()
                    .onStatus(status -> status.value() == 404, response ->
                            response.bodyToMono(String.class).map(msg -> new ResourceNotFoundException("Application ID '" + applicationId + "' not found in AI graph.")))
                    .onStatus(HttpStatusCode::is5xxServerError, response ->
                            response.bodyToMono(String.class).map(msg -> new AiServiceException("AI Service error during inference: " + msg)))
                    .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                    .block();
        } catch (WebClientResponseException.NotFound ex) {
            throw new ResourceNotFoundException("Application ID '" + applicationId + "' not found in AI graph.");
        } catch (WebClientRequestException ex) {
            log.error("Connection failed while requesting prediction for {}: {}", applicationId, ex.getMessage());
            throw new AiServiceException("Could not connect to Python AI Service at " + ex.getUri() + ": " + ex.getMessage(), ex);
        } catch (Exception ex) {
            if (ex instanceof ResourceNotFoundException rnfe) throw rnfe;
            log.error("Unexpected error during AI prediction for {}: {}", applicationId, ex.getMessage());
            throw new AiServiceException("AI inference request failed: " + ex.getMessage(), ex);
        }
    }

    public Map<String, Object> predictBatch(List<String> applicationIds) {
        try {
            Map<String, Object> payload = Collections.singletonMap("application_ids", applicationIds);
            return webClient.post()
                    .uri("/predict/batch")
                    .bodyValue(payload)
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, response ->
                            response.bodyToMono(String.class).map(msg -> new AiServiceException("AI Batch inference failed: " + msg)))
                    .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                    .block();
        } catch (WebClientRequestException ex) {
            log.error("Connection failed while requesting batch prediction: {}", ex.getMessage());
            throw new AiServiceException("Could not connect to Python AI Service: " + ex.getMessage(), ex);
        }
    }

    public Map<String, Object> getNeighborhood(String type, String id, int maxNeighbors) {
        try {
            return webClient.get()
                    .uri(uriBuilder -> uriBuilder
                            .path("/graph/neighborhood/{type}/{id}")
                            .queryParam("max_neighbors", maxNeighbors)
                            .build(type, id))
                    .retrieve()
                    .onStatus(status -> status.value() == 404, response ->
                            response.bodyToMono(String.class).map(msg -> new ResourceNotFoundException("Entity '" + id + "' of type '" + type + "' not found in AI graph.")))
                    .onStatus(status -> status.value() == 400, response ->
                            response.bodyToMono(String.class).map(IllegalArgumentException::new))
                    .onStatus(HttpStatusCode::is5xxServerError, response ->
                            response.bodyToMono(String.class).map(msg -> new AiServiceException("AI Graph query failed: " + msg)))
                    .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                    .block();
        } catch (WebClientResponseException.NotFound ex) {
            throw new ResourceNotFoundException("Entity '" + id + "' of type '" + type + "' not found in AI graph.");
        } catch (WebClientRequestException ex) {
            log.error("Connection failed while querying neighborhood for {}/{}: {}", type, id, ex.getMessage());
            throw new AiServiceException("Could not connect to Python AI Service: " + ex.getMessage(), ex);
        }
    }
}
