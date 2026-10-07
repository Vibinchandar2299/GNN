package com.hiregraph;

import com.hiregraph.entity.ModelBenchmark;
import com.hiregraph.repository.ModelBenchmarkRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class HireGraphApplicationTests {

    @Autowired
    private ModelBenchmarkRepository benchmarkRepository;

    @Test
    void contextLoads() {
        assertNotNull(benchmarkRepository, "Spring context should inject repositories");
    }

    @Test
    void flywayMigrationAndBenchmarksVerified() {
        Optional<ModelBenchmark> baselineOpt = benchmarkRepository.findByModelName("Standard GraphSAGE");
        assertTrue(baselineOpt.isPresent(), "Standard GraphSAGE benchmark should be seeded by Flyway");
        ModelBenchmark baseline = baselineOpt.get();
        assertEquals(0.8387, baseline.getAccuracy(), 0.001);
        assertEquals(0.8443, baseline.getPrecisionScore(), 0.001);
        assertEquals(0.8699, baseline.getRecall(), 0.001);
        assertEquals(0.8569, baseline.getF1Score(), 0.001);
        assertEquals(0.9140, baseline.getRocAuc(), 0.001);

        Optional<ModelBenchmark> amrgOpt = benchmarkRepository.findByModelName("AMRG-GraphSAGE");
        assertTrue(amrgOpt.isPresent(), "AMRG-GraphSAGE benchmark should be seeded by Flyway");
        ModelBenchmark amrg = amrgOpt.get();
        assertEquals(0.8427, amrg.getAccuracy(), 0.001);
        assertEquals(0.8493, amrg.getPrecisionScore(), 0.001);
        assertEquals(0.8714, amrg.getRecall(), 0.001);
        assertEquals(0.8602, amrg.getF1Score(), 0.001);
        assertEquals(0.9142, amrg.getRocAuc(), 0.001);
    }
}
