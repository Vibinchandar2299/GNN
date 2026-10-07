package com.hiregraph.controller;

import com.hiregraph.dto.response.CandidateResponse;
import com.hiregraph.service.CandidateService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/candidates")
public class CandidateController {

    private final CandidateService candidateService;

    public CandidateController(CandidateService candidateService) {
        this.candidateService = candidateService;
    }

    @GetMapping
    public ResponseEntity<Page<CandidateResponse>> getCandidates(
            @RequestParam(required = false) String department,
            @PageableDefault(size = 20) Pageable pageable) {
        return ResponseEntity.ok(candidateService.getCandidates(department, pageable));
    }

    @GetMapping("/{studentId}")
    public ResponseEntity<CandidateResponse> getCandidateById(@PathVariable String studentId) {
        return ResponseEntity.ok(candidateService.getCandidateById(studentId));
    }
}
