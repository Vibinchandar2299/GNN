package com.hiregraph.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "student_skills", uniqueConstraints = {
    @UniqueConstraint(name = "uq_student_skill", columnNames = {"student_id", "skill_id"})
})
public class StudentSkill {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "student_id", nullable = false, length = 50)
    private String studentId;

    @Column(name = "skill_id", nullable = false, length = 50)
    private String skillId;

    @Column(name = "skill_proficiency")
    private Double skillProficiency;

    public StudentSkill() {}

    public StudentSkill(String studentId, String skillId, Double skillProficiency) {
        this.studentId = studentId;
        this.skillId = skillId;
        this.skillProficiency = skillProficiency;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getStudentId() { return studentId; }
    public void setStudentId(String studentId) { this.studentId = studentId; }

    public String getSkillId() { return skillId; }
    public void setSkillId(String skillId) { this.skillId = skillId; }

    public Double getSkillProficiency() { return skillProficiency; }
    public void setSkillProficiency(Double skillProficiency) { this.skillProficiency = skillProficiency; }
}
