package com.hiregraph.controller;

import com.hiregraph.dto.response.JobResponse;
import com.hiregraph.service.JobService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/jobs")
public class JobController {

    private final JobService jobService;

    public JobController(JobService jobService) {
        this.jobService = jobService;
    }

    @GetMapping
    public ResponseEntity<Page<JobResponse>> getJobs(
            @RequestParam(required = false) String domain,
            @PageableDefault(size = 20) Pageable pageable) {
        return ResponseEntity.ok(jobService.getJobs(domain, pageable));
    }

    @GetMapping("/{jobId}")
    public ResponseEntity<JobResponse> getJobById(@PathVariable String jobId) {
        return ResponseEntity.ok(jobService.getJobById(jobId));
    }
}
