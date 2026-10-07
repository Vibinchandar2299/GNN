package com.hiregraph.repository;

import com.hiregraph.entity.Company;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface CompanyRepository extends JpaRepository<Company, Long> {
    Optional<Company> findByCompanyId(String companyId);
    boolean existsByCompanyId(String companyId);
    Page<Company> findByIndustryIgnoreCase(String industry, Pageable pageable);
}
