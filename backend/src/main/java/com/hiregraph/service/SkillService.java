package com.hiregraph.service;

import com.hiregraph.dto.response.SkillDemandResponse;
import com.hiregraph.dto.response.SkillResponse;
import com.hiregraph.entity.Skill;
import com.hiregraph.mapper.EntityDtoMapper;
import com.hiregraph.repository.JobSkillRepository;
import com.hiregraph.repository.SkillRepository;
import com.hiregraph.repository.StudentSkillRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@Transactional(readOnly = true)
public class SkillService {

    private final SkillRepository skillRepository;
    private final StudentSkillRepository studentSkillRepository;
    private final JobSkillRepository jobSkillRepository;

    public SkillService(SkillRepository skillRepository,
                        StudentSkillRepository studentSkillRepository,
                        JobSkillRepository jobSkillRepository) {
        this.skillRepository = skillRepository;
        this.studentSkillRepository = studentSkillRepository;
        this.jobSkillRepository = jobSkillRepository;
    }

    public List<SkillResponse> getAllSkills() {
        List<Skill> skills = skillRepository.findAll();
        return skills.stream().map(skill -> {
            long studentCount = studentSkillRepository.countBySkillId(skill.getSkillId());
            long jobCount = jobSkillRepository.countBySkillId(skill.getSkillId());
            return EntityDtoMapper.toSkillResponse(skill, studentCount, jobCount);
        }).toList();
    }

    public List<SkillDemandResponse> getSkillDemand() {
        List<Skill> skills = skillRepository.findAll();
        List<SkillDemandResponse> demandList = new ArrayList<>();

        for (Skill skill : skills) {
            long supply = studentSkillRepository.countBySkillId(skill.getSkillId());
            long demand = jobSkillRepository.countBySkillId(skill.getSkillId());
            double ratio = supply > 0 ? (double) demand / supply : (demand > 0 ? 1.0 : 0.0);
            double roundedRatio = Math.round(ratio * 1000.0) / 1000.0;

            demandList.add(new SkillDemandResponse(
                    skill.getSkillId(),
                    skill.getSkillName(),
                    demand,
                    supply,
                    roundedRatio
            ));
        }

        // Sort by demand descending
        demandList.sort((a, b) -> Long.compare(b.getDemandCount(), a.getDemandCount()));
        return demandList;
    }
}
