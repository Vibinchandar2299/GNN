package com.hiregraph.repository;

import com.hiregraph.entity.JobSkill;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface JobSkillRepository extends JpaRepository<JobSkill, Long> {
    List<JobSkill> findByJobId(String jobId);
    List<JobSkill> findBySkillId(String skillId);
    long countBySkillId(String skillId);

    @Query("SELECT js.skillId, COUNT(js) FROM JobSkill js GROUP BY js.skillId ORDER BY COUNT(js) DESC")
    List<Object[]> countJobsPerSkill();
}
