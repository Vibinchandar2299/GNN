package com.hiregraph.service;

import com.hiregraph.dto.response.JobResponse;
import com.hiregraph.entity.Job;
import com.hiregraph.entity.Skill;
import com.hiregraph.exception.ResourceNotFoundException;
import com.hiregraph.mapper.EntityDtoMapper;
import com.hiregraph.repository.JobRepository;
import com.hiregraph.repository.JobSkillRepository;
import com.hiregraph.repository.SkillRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@Transactional(readOnly = true)
public class JobService {

    private final JobRepository jobRepository;
    private final JobSkillRepository jobSkillRepository;
    private final SkillRepository skillRepository;

    public JobService(JobRepository jobRepository,
                      JobSkillRepository jobSkillRepository,
                      SkillRepository skillRepository) {
        this.jobRepository = jobRepository;
        this.jobSkillRepository = jobSkillRepository;
        this.skillRepository = skillRepository;
    }

    public Page<JobResponse> getJobs(String domain, Pageable pageable) {
        Page<Job> page;
        if (domain != null && !domain.isBlank()) {
            page = jobRepository.findByJobDomainIgnoreCase(domain.trim(), pageable);
        } else {
            page = jobRepository.findAll(pageable);
        }

        Map<String, String> skillNames = skillRepository.findAll().stream()
                .collect(Collectors.toMap(Skill::getSkillId, Skill::getSkillName, (a, b) -> a));

        return page.map(job -> {
            List<String> requiredSkills = jobSkillRepository.findByJobId(job.getJobId()).stream()
                    .map(js -> skillNames.getOrDefault(js.getSkillId(), js.getSkillId()))
                    .toList();
            return EntityDtoMapper.toJobResponse(job, requiredSkills);
        });
    }

    public JobResponse getJobById(String jobId) {
        Job job = jobRepository.findByJobId(jobId.trim())
                .orElseThrow(() -> new ResourceNotFoundException("Job with ID '" + jobId + "' not found."));

        Map<String, String> skillNames = skillRepository.findAll().stream()
                .collect(Collectors.toMap(Skill::getSkillId, Skill::getSkillName, (a, b) -> a));

        List<String> requiredSkills = jobSkillRepository.findByJobId(job.getJobId()).stream()
                .map(js -> skillNames.getOrDefault(js.getSkillId(), js.getSkillId()))
                .toList();

        return EntityDtoMapper.toJobResponse(job, requiredSkills);
    }
}
