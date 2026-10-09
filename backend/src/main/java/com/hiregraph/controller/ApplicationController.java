package com.hiregraph.controller;

import com.hiregraph.dto.request.PredictionRequest;
import com.hiregraph.dto.response.ApplicationResponse;
import com.hiregraph.dto.response.PredictionResponse;
import com.hiregraph.service.ApplicationService;
import com.hiregraph.service.PredictionService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/applications")
public class ApplicationController {

    private final ApplicationService applicationService;
    private final PredictionService predictionService;

    public ApplicationController(ApplicationService applicationService,
                                 PredictionService predictionService) {
        this.applicationService = applicationService;
        this.predictionService = predictionService;
    }

    @GetMapping
    public ResponseEntity<Page<ApplicationResponse>> getApplications(
            @RequestParam(required = false) Integer cycle,
            @RequestParam(required = false) Integer finalStatus,
            @PageableDefault(size = 20) Pageable pageable) {
        return ResponseEntity.ok(applicationService.getApplications(cycle, finalStatus, pageable));
    }

    @GetMapping("/{applicationId}")
    public ResponseEntity<ApplicationResponse> getApplicationById(@PathVariable String applicationId) {
        return ResponseEntity.ok(applicationService.getApplicationById(applicationId));
    }

    @PostMapping("/{applicationId}/predict")
    public ResponseEntity<PredictionResponse> predictApplication(
            @PathVariable String applicationId,
            @RequestBody(required = false) PredictionRequest request) {
        return ResponseEntity.ok(predictionService.predictApplication(applicationId, request));
    }

    @PostMapping("/predict/batch")
    public ResponseEntity<com.hiregraph.dto.response.BatchPredictionResponse> predictBatch(
            @RequestBody com.hiregraph.dto.request.BatchPredictionRequest request) {
        return ResponseEntity.ok(predictionService.predictBatch(request));
    }
}
