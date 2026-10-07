package com.hiregraph.service;

import com.hiregraph.dto.response.CandidateResponse;
import com.hiregraph.entity.Skill;
import com.hiregraph.entity.Student;
import com.hiregraph.entity.StudentSkill;
import com.hiregraph.exception.ResourceNotFoundException;
import com.hiregraph.mapper.EntityDtoMapper;
import com.hiregraph.repository.SkillRepository;
import com.hiregraph.repository.StudentRepository;
import com.hiregraph.repository.StudentSkillRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@Transactional(readOnly = true)
public class CandidateService {

    private final StudentRepository studentRepository;
    private final StudentSkillRepository studentSkillRepository;
    private final SkillRepository skillRepository;

    public CandidateService(StudentRepository studentRepository,
                            StudentSkillRepository studentSkillRepository,
                            SkillRepository skillRepository) {
        this.studentRepository = studentRepository;
        this.studentSkillRepository = studentSkillRepository;
        this.skillRepository = skillRepository;
    }

    public Page<CandidateResponse> getCandidates(String department, Pageable pageable) {
        Page<Student> page;
        if (department != null && !department.isBlank()) {
            page = studentRepository.findByDepartmentIgnoreCase(department.trim(), pageable);
        } else {
            page = studentRepository.findAll(pageable);
        }

        Map<String, String> skillNames = skillRepository.findAll().stream()
                .collect(Collectors.toMap(Skill::getSkillId, Skill::getSkillName, (a, b) -> a));

        return page.map(student -> {
            List<String> skills = studentSkillRepository.findByStudentId(student.getStudentId()).stream()
                    .map(ss -> skillNames.getOrDefault(ss.getSkillId(), ss.getSkillId()))
                    .toList();
            return EntityDtoMapper.toCandidateResponse(student, skills);
        });
    }

    public CandidateResponse getCandidateById(String studentId) {
        Student student = studentRepository.findByStudentId(studentId.trim())
                .orElseThrow(() -> new ResourceNotFoundException("Student with ID '" + studentId + "' not found."));

        Map<String, String> skillNames = skillRepository.findAll().stream()
                .collect(Collectors.toMap(Skill::getSkillId, Skill::getSkillName, (a, b) -> a));

        List<String> skills = studentSkillRepository.findByStudentId(student.getStudentId()).stream()
                .map(ss -> skillNames.getOrDefault(ss.getSkillId(), ss.getSkillId()))
                .toList();

        return EntityDtoMapper.toCandidateResponse(student, skills);
    }
}
