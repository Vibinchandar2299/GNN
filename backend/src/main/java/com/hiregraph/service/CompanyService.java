package com.hiregraph.service;

import com.hiregraph.dto.response.CompanyResponse;
import com.hiregraph.entity.Company;
import com.hiregraph.exception.ResourceNotFoundException;
import com.hiregraph.mapper.EntityDtoMapper;
import com.hiregraph.repository.ApplicationRepository;
import com.hiregraph.repository.CompanyRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class CompanyService {

    private final CompanyRepository companyRepository;
    private final ApplicationRepository applicationRepository;

    public CompanyService(CompanyRepository companyRepository, ApplicationRepository applicationRepository) {
        this.companyRepository = companyRepository;
        this.applicationRepository = applicationRepository;
    }

    public Page<CompanyResponse> getCompanies(String industry, Pageable pageable) {
        Page<Company> page;
        if (industry != null && !industry.isBlank()) {
            page = companyRepository.findByIndustryIgnoreCase(industry.trim(), pageable);
        } else {
            page = companyRepository.findAll(pageable);
        }

        return page.map(company -> {
            long appCount = applicationRepository.findByCompanyId(company.getCompanyId()).size();
            return EntityDtoMapper.toCompanyResponse(company, appCount);
        });
    }

    public CompanyResponse getCompanyById(String companyId) {
        Company company = companyRepository.findByCompanyId(companyId.trim())
                .orElseThrow(() -> new ResourceNotFoundException("Company with ID '" + companyId + "' not found."));

        long appCount = applicationRepository.findByCompanyId(company.getCompanyId()).size();
        return EntityDtoMapper.toCompanyResponse(company, appCount);
    }
}
