package com.hiregraph.controller;

import com.hiregraph.dto.response.CompanyResponse;
import com.hiregraph.service.CompanyService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/companies")
public class CompanyController {

    private final CompanyService companyService;

    public CompanyController(CompanyService companyService) {
        this.companyService = companyService;
    }

    @GetMapping
    public ResponseEntity<Page<CompanyResponse>> getCompanies(
            @RequestParam(required = false) String industry,
            @PageableDefault(size = 20) Pageable pageable) {
        return ResponseEntity.ok(companyService.getCompanies(industry, pageable));
    }

    @GetMapping("/{companyId}")
    public ResponseEntity<CompanyResponse> getCompanyById(@PathVariable String companyId) {
        return ResponseEntity.ok(companyService.getCompanyById(companyId));
    }
}
