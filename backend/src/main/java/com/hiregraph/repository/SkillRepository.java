package com.hiregraph.repository;

import com.hiregraph.entity.Skill;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface SkillRepository extends JpaRepository<Skill, Long> {
    Optional<Skill> findBySkillId(String skillId);
    boolean existsBySkillId(String skillId);
}
