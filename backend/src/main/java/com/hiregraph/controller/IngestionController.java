package com.hiregraph.controller;

import com.hiregraph.dto.response.IngestionResultResponse;
import com.hiregraph.service.DataIngestionService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/admin")
public class IngestionController {

    private final DataIngestionService dataIngestionService;

    public IngestionController(DataIngestionService dataIngestionService) {
        this.dataIngestionService = dataIngestionService;
    }

    @PostMapping("/ingest")
    public ResponseEntity<IngestionResultResponse> triggerIngestion(
            @RequestParam(defaultValue = "false") boolean forceReload) {
        return ResponseEntity.ok(dataIngestionService.ingestData(forceReload));
    }
}
