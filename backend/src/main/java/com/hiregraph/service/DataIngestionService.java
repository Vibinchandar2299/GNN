package com.hiregraph.service;

import com.hiregraph.dto.response.IngestionResultResponse;
import com.hiregraph.entity.*;
import com.hiregraph.exception.IngestionException;
import com.hiregraph.repository.*;
import org.apache.poi.ss.usermodel.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.File;
import java.io.FileInputStream;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

@Service
public class DataIngestionService {

    private static final Logger log = LoggerFactory.getLogger(DataIngestionService.class);

    private final StudentRepository studentRepository;
    private final CompanyRepository companyRepository;
    private final JobRepository jobRepository;
    private final SkillRepository skillRepository;
    private final StudentSkillRepository studentSkillRepository;
    private final JobSkillRepository jobSkillRepository;
    private final ApplicationRepository applicationRepository;

    @Value("${hiregraph.dataset.path:../Dataset/GNN_Placement_Dataset.xlsx}")
    private String datasetPathConfig;

    public DataIngestionService(StudentRepository studentRepository,
                                CompanyRepository companyRepository,
                                JobRepository jobRepository,
                                SkillRepository skillRepository,
                                StudentSkillRepository studentSkillRepository,
                                JobSkillRepository jobSkillRepository,
                                ApplicationRepository applicationRepository) {
        this.studentRepository = studentRepository;
        this.companyRepository = companyRepository;
        this.jobRepository = jobRepository;
        this.skillRepository = skillRepository;
        this.studentSkillRepository = studentSkillRepository;
        this.jobSkillRepository = jobSkillRepository;
        this.applicationRepository = applicationRepository;
    }

    private File resolveDatasetFile() {
        File file = new File(datasetPathConfig);
        if (file.exists()) return file;

        // Try direct paths relative to workspace root
        Path currentDir = Paths.get("").toAbsolutePath();
        File candidate1 = currentDir.resolve("Dataset/GNN_Placement_Dataset.xlsx").toFile();
        if (candidate1.exists()) return candidate1;

        File candidate2 = currentDir.resolve("../Dataset/GNN_Placement_Dataset.xlsx").toFile();
        if (candidate2.exists()) return candidate2;

        File candidate3 = new File("c:/Users/VIBIN/Vibin Projects/GNN/Dataset/GNN_Placement_Dataset.xlsx");
        if (candidate3.exists()) return candidate3;

        throw new IngestionException("Dataset file not found at " + datasetPathConfig + " or fallback paths.");
    }

    @Transactional
    public IngestionResultResponse ingestData(boolean forceReload) {
        long existingApps = applicationRepository.count();
        if (existingApps > 0 && !forceReload) {
            log.info("Dataset already ingested (found {} applications). Skipping ingestion.", existingApps);
            return new IngestionResultResponse(
                    "SKIPPED",
                    existingApps,
                    studentRepository.count(),
                    companyRepository.count(),
                    jobRepository.count(),
                    skillRepository.count(),
                    applicationRepository.countByFinalStatus(1),
                    applicationRepository.countByFinalStatus(0),
                    "Dataset already populated in PostgreSQL. Use forceReload=true to re-ingest."
            );
        }

        File excelFile = resolveDatasetFile();
        log.info("Starting controlled data ingestion from: {}", excelFile.getAbsolutePath());

        try (FileInputStream fis = new FileInputStream(excelFile);
             Workbook workbook = WorkbookFactory.create(fis)) {

            Sheet unifiedSheet = workbook.getSheet("unified_dataset");
            if (unifiedSheet == null) {
                throw new IngestionException("Sheet 'unified_dataset' not found in workbook.");
            }

            Sheet edgesSheet = workbook.getSheet("graph_edges");
            if (edgesSheet == null) {
                throw new IngestionException("Sheet 'graph_edges' not found in workbook.");
            }

            // 1. Read and validate unified_dataset
            Map<String, Integer> colIndex = getColumnIndexMap(unifiedSheet.getRow(0));

            Map<String, Student> studentsMap = new LinkedHashMap<>();
            Map<String, Company> companiesMap = new LinkedHashMap<>();
            Map<String, Job> jobsMap = new LinkedHashMap<>();
            List<Application> applications = new ArrayList<>();

            int selectedCount = 0;
            int rejectedCount = 0;
            int cycle2023Count = 0;
            int cycle2024Count = 0;
            int cycle2025Count = 0;
            int cycle2026Count = 0;

            int rowCount = unifiedSheet.getLastRowNum();
            for (int r = 1; r <= rowCount; r++) {
                Row row = unifiedSheet.getRow(r);
                if (row == null) continue;

                String appId = getString(row, colIndex.get("application_id"));
                String studentId = getString(row, colIndex.get("student_id"));
                String companyId = getString(row, colIndex.get("company_id"));
                String jobId = getString(row, colIndex.get("job_id"));
                int cycle = (int) getNumeric(row, colIndex.get("recruitment_cycle"));
                int finalStatus = (int) getNumeric(row, colIndex.get("final_status"));

                if (finalStatus == 1) selectedCount++;
                else if (finalStatus == 0) rejectedCount++;

                if (cycle == 2023) cycle2023Count++;
                else if (cycle == 2024) cycle2024Count++;
                else if (cycle == 2025) cycle2025Count++;
                else if (cycle == 2026) cycle2026Count++;

                // Student
                if (!studentsMap.containsKey(studentId)) {
                    studentsMap.put(studentId, new Student(
                            studentId,
                            getString(row, colIndex.get("department")),
                            getNumeric(row, colIndex.get("cgpa")),
                            (int) getNumeric(row, colIndex.get("backlogs")),
                            getNumeric(row, colIndex.get("aptitude_score_pre")),
                            getNumeric(row, colIndex.get("coding_score_pre")),
                            getNumeric(row, colIndex.get("communication_score_pre")),
                            (int) getNumeric(row, colIndex.get("projects_count")),
                            (int) getNumeric(row, colIndex.get("internships_count")),
                            (int) getNumeric(row, colIndex.get("certifications_count")),
                            getNumeric(row, colIndex.get("resume_score"))
                    ));
                }

                // Company
                if (!companiesMap.containsKey(companyId)) {
                    companiesMap.put(companyId, new Company(
                            companyId,
                            "Company " + companyId,
                            getString(row, colIndex.get("industry")),
                            getString(row, colIndex.get("company_size")),
                            getNumeric(row, colIndex.get("historical_selection_rate")),
                            getNumeric(row, colIndex.get("historical_average_selected_cgpa"))
                    ));
                }

                // Job
                if (!jobsMap.containsKey(jobId)) {
                    jobsMap.put(jobId, new Job(
                            jobId,
                            getString(row, colIndex.get("job_title")),
                            getString(row, colIndex.get("job_domain")),
                            getNumeric(row, colIndex.get("minimum_cgpa")),
                            (int) getNumeric(row, colIndex.get("experience_required_months")),
                            getNumeric(row, colIndex.get("salary_lpa")),
                            (int) getNumeric(row, colIndex.get("required_skill_count"))
                    ));
                }

                // Application
                applications.add(new Application(
                        appId,
                        studentId,
                        companyId,
                        jobId,
                        cycle,
                        getNumeric(row, colIndex.get("relevant_experience_months")),
                        (int) getNumeric(row, colIndex.get("total_skill_count")),
                        getNumeric(row, colIndex.get("average_skill_proficiency")),
                        getNumeric(row, colIndex.get("role_shift_score")),
                        getNumeric(row, colIndex.get("skill_match_ratio")),
                        getNumeric(row, colIndex.get("required_skill_level_gap")),
                        getNumeric(row, colIndex.get("role_experience_match")),
                        (int) getNumeric(row, colIndex.get("expected_hiring_count")),
                        finalStatus
                ));
            }

            // 2. Read graph_edges for skills and relationships
            Map<String, Integer> edgeColIndex = getColumnIndexMap(edgesSheet.getRow(0));
            Map<String, Skill> skillsMap = new LinkedHashMap<>();
            List<StudentSkill> studentSkills = new ArrayList<>();
            List<JobSkill> jobSkills = new ArrayList<>();

            int edgeRowCount = edgesSheet.getLastRowNum();
            for (int r = 1; r <= edgeRowCount; r++) {
                Row row = edgesSheet.getRow(r);
                if (row == null) continue;

                String src = getString(row, edgeColIndex.get("source_id"));
                String rel = getString(row, edgeColIndex.get("relation_type"));
                String dst = getString(row, edgeColIndex.get("target_id"));

                if (src.startsWith("SK_") && !skillsMap.containsKey(src)) {
                    skillsMap.put(src, new Skill(src, "Skill " + src));
                }
                if (dst.startsWith("SK_") && !skillsMap.containsKey(dst)) {
                    skillsMap.put(dst, new Skill(dst, "Skill " + dst));
                }

                if ("HAS_SKILL".equals(rel)) {
                    studentSkills.add(new StudentSkill(src, dst, 1.0));
                } else if ("REQUIRES_SKILL".equals(rel)) {
                    jobSkills.add(new JobSkill(src, dst, 1.0));
                }
            }

            // ==============================================================
            // STRICT PRE-INSERT VALIDATION AGAINST RESEARCH GROUND TRUTH
            // ==============================================================
            log.info("Validating parsed dataset counts...");
            assertCount("Applications", applications.size(), 4000);
            assertCount("Students", studentsMap.size(), 1534);
            assertCount("Companies", companiesMap.size(), 125);
            assertCount("Jobs", jobsMap.size(), 300);
            assertCount("Skills", skillsMap.size(), 18);

            assertCount("Selected Applications", selectedCount, 2200);
            assertCount("Rejected Applications", rejectedCount, 1800);

            assertCount("Cycle 2023-2024 (Train)", cycle2023Count + cycle2024Count, 1594);
            assertCount("Cycle 2025 (Validation)", cycle2025Count, 1160);
            assertCount("Cycle 2026 (Test)", cycle2026Count, 1246);

            log.info("All pre-insert validation assertions PASSED.");

            // Clear existing data if force reloading
            if (forceReload && existingApps > 0) {
                log.warn("Force reload requested. Clearing existing database records...");
                applicationRepository.deleteAllInBatch();
                studentSkillRepository.deleteAllInBatch();
                jobSkillRepository.deleteAllInBatch();
                studentRepository.deleteAllInBatch();
                jobRepository.deleteAllInBatch();
                companyRepository.deleteAllInBatch();
                skillRepository.deleteAllInBatch();
            }

            // Batch insert entities
            log.info("Inserting 18 skills...");
            skillRepository.saveAll(skillsMap.values());

            log.info("Inserting 1534 students...");
            studentRepository.saveAll(studentsMap.values());

            log.info("Inserting 125 companies...");
            companyRepository.saveAll(companiesMap.values());

            log.info("Inserting 300 jobs...");
            jobRepository.saveAll(jobsMap.values());

            log.info("Inserting {} student skills...", studentSkills.size());
            studentSkillRepository.saveAll(studentSkills);

            log.info("Inserting {} job skills...", jobSkills.size());
            jobSkillRepository.saveAll(jobSkills);

            log.info("Inserting 4000 applications...");
            applicationRepository.saveAll(applications);

            log.info("Controlled data ingestion completed successfully!");

            return new IngestionResultResponse(
                    "SUCCESS",
                    applications.size(),
                    studentsMap.size(),
                    companiesMap.size(),
                    jobsMap.size(),
                    skillsMap.size(),
                    selectedCount,
                    rejectedCount,
                    "Successfully ingested and verified all 4000 applications and graph entities in PostgreSQL."
            );

        } catch (Exception ex) {
            log.error("Ingestion failed: {}", ex.getMessage(), ex);
            throw new IngestionException("Data ingestion error: " + ex.getMessage(), ex);
        }
    }

    private void assertCount(String entity, int actual, int expected) {
        if (actual != expected) {
            throw new IngestionException(String.format("Validation failed for %s: expected %d, got %d", entity, expected, actual));
        }
    }

    private Map<String, Integer> getColumnIndexMap(Row headerRow) {
        Map<String, Integer> map = new HashMap<>();
        for (Cell cell : headerRow) {
            map.put(cell.getStringCellValue().trim(), cell.getColumnIndex());
        }
        return map;
    }

    private String getString(Row row, Integer colIdx) {
        if (colIdx == null) return "";
        Cell cell = row.getCell(colIdx);
        if (cell == null) return "";
        if (cell.getCellType() == CellType.STRING) return cell.getStringCellValue().trim();
        if (cell.getCellType() == CellType.NUMERIC) return String.valueOf((long) cell.getNumericCellValue());
        return cell.toString().trim();
    }

    private double getNumeric(Row row, Integer colIdx) {
        if (colIdx == null) return 0.0;
        Cell cell = row.getCell(colIdx);
        if (cell == null) return 0.0;
        if (cell.getCellType() == CellType.NUMERIC) return cell.getNumericCellValue();
        if (cell.getCellType() == CellType.STRING) {
            try {
                return Double.parseDouble(cell.getStringCellValue().trim());
            } catch (NumberFormatException e) {
                return 0.0;
            }
        }
        return 0.0;
    }
}
