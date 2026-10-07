package com.hiregraph.controller;

import com.hiregraph.dto.response.HiringTrendResponse;
import com.hiregraph.service.AnalyticsService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/v1/analytics")
public class AnalyticsController {

    private final AnalyticsService analyticsService;

    public AnalyticsController(AnalyticsService analyticsService) {
        this.analyticsService = analyticsService;
    }

    @GetMapping("/trends")
    public ResponseEntity<List<HiringTrendResponse>> getTrends() {
        return ResponseEntity.ok(analyticsService.getTrends());
    }
}
