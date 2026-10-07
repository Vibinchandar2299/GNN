package com.hiregraph.controller;

import com.hiregraph.dto.response.SkillDemandResponse;
import com.hiregraph.dto.response.SkillResponse;
import com.hiregraph.service.SkillService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/v1/skills")
public class SkillController {

    private final SkillService skillService;

    public SkillController(SkillService skillService) {
        this.skillService = skillService;
    }

    @GetMapping
    public ResponseEntity<List<SkillResponse>> getAllSkills() {
        return ResponseEntity.ok(skillService.getAllSkills());
    }

    @GetMapping("/demand")
    public ResponseEntity<List<SkillDemandResponse>> getSkillDemand() {
        return ResponseEntity.ok(skillService.getSkillDemand());
    }
}
