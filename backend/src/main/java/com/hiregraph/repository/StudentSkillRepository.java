package com.hiregraph.repository;

import com.hiregraph.entity.StudentSkill;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface StudentSkillRepository extends JpaRepository<StudentSkill, Long> {
    List<StudentSkill> findByStudentId(String studentId);
    List<StudentSkill> findBySkillId(String skillId);
    long countBySkillId(String skillId);

    @Query("SELECT ss.skillId, COUNT(ss) FROM StudentSkill ss GROUP BY ss.skillId ORDER BY COUNT(ss) DESC")
    List<Object[]> countStudentsPerSkill();
}
