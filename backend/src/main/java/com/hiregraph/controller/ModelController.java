package com.hiregraph.controller;

import com.hiregraph.dto.response.ModelBenchmarkResponse;
import com.hiregraph.dto.response.ModelMetadataResponse;
import com.hiregraph.service.ModelService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/v1/model")
public class ModelController {

    private final ModelService modelService;

    public ModelController(ModelService modelService) {
        this.modelService = modelService;
    }

    @GetMapping("/benchmarks")
    public ResponseEntity<List<ModelBenchmarkResponse>> getBenchmarks() {
        return ResponseEntity.ok(modelService.getBenchmarks());
    }

    @GetMapping("/metadata")
    public ResponseEntity<ModelMetadataResponse> getMetadata() {
        return ResponseEntity.ok(modelService.getMetadata());
    }
}
