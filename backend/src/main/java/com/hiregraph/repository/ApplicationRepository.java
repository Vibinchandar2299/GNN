package com.hiregraph.repository;

import com.hiregraph.entity.Application;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ApplicationRepository extends JpaRepository<Application, Long> {
    Optional<Application> findByApplicationId(String applicationId);
    boolean existsByApplicationId(String applicationId);

    List<Application> findByStudentId(String studentId);
    List<Application> findByCompanyId(String companyId);
    List<Application> findByJobId(String jobId);

    Page<Application> findByCycle(Integer cycle, Pageable pageable);
    Page<Application> findByFinalStatus(Integer finalStatus, Pageable pageable);
    Page<Application> findByCycleAndFinalStatus(Integer cycle, Integer finalStatus, Pageable pageable);

    long countByFinalStatus(Integer finalStatus);
    long countByCycle(Integer cycle);
    long countByCycleAndFinalStatus(Integer cycle, Integer finalStatus);

    @Query("SELECT DISTINCT a.cycle FROM Application a ORDER BY a.cycle ASC")
    List<Integer> findDistinctCycles();

    @Query("SELECT a.cycle, a.finalStatus, COUNT(a) FROM Application a GROUP BY a.cycle, a.finalStatus ORDER BY a.cycle ASC, a.finalStatus ASC")
    List<Object[]> countGroupedByCycleAndFinalStatus();
}
