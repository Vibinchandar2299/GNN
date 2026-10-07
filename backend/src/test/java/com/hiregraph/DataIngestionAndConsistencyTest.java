package com.hiregraph;

import com.hiregraph.dto.response.IngestionResultResponse;
import com.hiregraph.repository.*;
import com.hiregraph.service.DataIngestionService;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class DataIngestionAndConsistencyTest {

    @Autowired
    private DataIngestionService ingestionService;

    @Autowired
    private StudentRepository studentRepository;

    @Autowired
    private CompanyRepository companyRepository;

    @Autowired
    private JobRepository jobRepository;

    @Autowired
    private SkillRepository skillRepository;

    @Autowired
    private ApplicationRepository applicationRepository;

    @Test
    @Order(1)
    void testControlledDataIngestionExecution() {
        IngestionResultResponse response = ingestionService.ingestData(false);
        assertNotNull(response);
        assertTrue("SUCCESS".equals(response.getStatus()) || "SKIPPED".equals(response.getStatus()));
    }

    @Test
    @Order(2)
    void testStrictRowCountsConsistency() {
        long studentCount = studentRepository.count();
        long companyCount = companyRepository.count();
        long jobCount = jobRepository.count();
        long skillCount = skillRepository.count();
        long appCount = applicationRepository.count();

        System.out.println("==================================================");
        System.out.println("VERIFIED POSTGRESQL ROW COUNTS:");
        System.out.println("  Students:     " + studentCount + " (Expected: 1534)");
        System.out.println("  Companies:    " + companyCount + " (Expected: 125)");
        System.out.println("  Jobs:         " + jobCount + " (Expected: 300)");
        System.out.println("  Skills:       " + skillCount + " (Expected: 18)");
        System.out.println("  Applications: " + appCount + " (Expected: 4000)");
        System.out.println("==================================================");

        assertEquals(1534, studentCount, "Students count mismatch!");
        assertEquals(125, companyCount, "Companies count mismatch!");
        assertEquals(300, jobCount, "Jobs count mismatch!");
        assertEquals(18, skillCount, "Skills count mismatch!");
        assertEquals(4000, appCount, "Applications count mismatch!");
    }

    @Test
    @Order(3)
    void testHistoricalOutcomesConsistency() {
        long selected = applicationRepository.countByFinalStatus(1);
        long rejected = applicationRepository.countByFinalStatus(0);

        System.out.println("==================================================");
        System.out.println("VERIFIED OUTCOME DISTRIBUTION:");
        System.out.println("  Selected: " + selected + " (Expected: 2200)");
        System.out.println("  Rejected: " + rejected + " (Expected: 1800)");
        System.out.println("==================================================");

        assertEquals(2200, selected, "Selected outcome count mismatch!");
        assertEquals(1800, rejected, "Rejected outcome count mismatch!");
    }

    @Test
    @Order(4)
    void testTemporalCyclesConsistency() {
        long cycle2023 = applicationRepository.countByCycle(2023);
        long cycle2024 = applicationRepository.countByCycle(2024);
        long cycle2025 = applicationRepository.countByCycle(2025);
        long cycle2026 = applicationRepository.countByCycle(2026);

        long trainTotal = cycle2023 + cycle2024;

        System.out.println("==================================================");
        System.out.println("VERIFIED TEMPORAL SPLIT COUNTS:");
        System.out.println("  2023: " + cycle2023);
        System.out.println("  2024: " + cycle2024);
        System.out.println("  Train (2023+2024): " + trainTotal + " (Expected: 1594)");
        System.out.println("  Validation (2025): " + cycle2025 + " (Expected: 1160)");
        System.out.println("  Testing (2026):    " + cycle2026 + " (Expected: 1246)");
        System.out.println("==================================================");

        assertEquals(1594, trainTotal, "Training cycle (2023+2024) count mismatch!");
        assertEquals(1160, cycle2025, "Validation cycle (2025) count mismatch!");
        assertEquals(1246, cycle2026, "Testing cycle (2026) count mismatch!");
    }
}
