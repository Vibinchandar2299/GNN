package com.hiregraph.service;

import com.hiregraph.dto.response.DashboardSummaryResponse;
import com.hiregraph.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class DashboardService {

    private final ApplicationRepository applicationRepository;
    private final StudentRepository studentRepository;
    private final CompanyRepository companyRepository;
    private final JobRepository jobRepository;
    private final SkillRepository skillRepository;

    public DashboardService(ApplicationRepository applicationRepository,
                            StudentRepository studentRepository,
                            CompanyRepository companyRepository,
                            JobRepository jobRepository,
                            SkillRepository skillRepository) {
        this.applicationRepository = applicationRepository;
        this.studentRepository = studentRepository;
        this.companyRepository = companyRepository;
        this.jobRepository = jobRepository;
        this.skillRepository = skillRepository;
    }

    public DashboardSummaryResponse getSummary() {
        long totalApps = applicationRepository.count();
        long totalStudents = studentRepository.count();
        long totalCompanies = companyRepository.count();
        long totalJobs = jobRepository.count();
        long totalSkills = skillRepository.count();
        long selected = applicationRepository.countByFinalStatus(1);
        long rejected = applicationRepository.countByFinalStatus(0);
        double rate = totalApps > 0 ? (double) selected / totalApps : 0.0;

        return new DashboardSummaryResponse(
                totalApps,
                totalStudents,
                totalCompanies,
                totalJobs,
                totalSkills,
                selected,
                rejected,
                Math.round(rate * 10000.0) / 10000.0
        );
    }
}
