package com.hiregraph.repository;

import com.hiregraph.entity.Job;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface JobRepository extends JpaRepository<Job, Long> {
    Optional<Job> findByJobId(String jobId);
    boolean existsByJobId(String jobId);
    Page<Job> findByJobDomainIgnoreCase(String jobDomain, Pageable pageable);
}
