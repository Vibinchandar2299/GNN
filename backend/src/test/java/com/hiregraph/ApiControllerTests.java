package com.hiregraph;

import com.hiregraph.service.DataIngestionService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
public class ApiControllerTests {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private DataIngestionService ingestionService;

    @BeforeEach
    void setup() {
        ingestionService.ingestData(false);
    }

    @Test
    void testDashboardSummary() throws Exception {
        mockMvc.perform(get("/api/v1/dashboard/summary"))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.totalApplications", is(4000)))
                .andExpect(jsonPath("$.totalStudents", is(1534)))
                .andExpect(jsonPath("$.totalCompanies", is(125)))
                .andExpect(jsonPath("$.totalJobs", is(300)))
                .andExpect(jsonPath("$.totalSkills", is(18)))
                .andExpect(jsonPath("$.selectedCount", is(2200)))
                .andExpect(jsonPath("$.rejectedCount", is(1800)))
                .andExpect(jsonPath("$.selectionRate", is(0.55)));
    }

    @Test
    void testCandidatesListAndDetail() throws Exception {
        mockMvc.perform(get("/api/v1/candidates?page=0&size=5"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content", hasSize(5)));

        mockMvc.perform(get("/api/v1/candidates/S1654"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.studentId", is("S1654")))
                .andExpect(jsonPath("$.skills", not(empty())));

        mockMvc.perform(get("/api/v1/candidates/NON_EXISTENT_STUDENT"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.error", is("RESOURCE_NOT_FOUND")));
    }

    @Test
    void testCompaniesListAndDetail() throws Exception {
        mockMvc.perform(get("/api/v1/companies?page=0&size=5"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content", hasSize(5)));

        mockMvc.perform(get("/api/v1/companies/C014"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.companyId", is("C014")))
                .andExpect(jsonPath("$.industry", notNullValue()));
    }

    @Test
    void testJobsListAndDetail() throws Exception {
        mockMvc.perform(get("/api/v1/jobs?page=0&size=5"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content", hasSize(5)));

        mockMvc.perform(get("/api/v1/jobs/J0263"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.jobId", is("J0263")))
                .andExpect(jsonPath("$.salaryLpa", notNullValue()));
    }

    @Test
    void testSkillsListAndDemand() throws Exception {
        mockMvc.perform(get("/api/v1/skills"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(18)));

        mockMvc.perform(get("/api/v1/skills/demand"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(18)))
                .andExpect(jsonPath("$[0].demandCount", greaterThanOrEqualTo(0)));
    }

    @Test
    void testApplicationsListAndDetail() throws Exception {
        mockMvc.perform(get("/api/v1/applications?page=0&size=10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content", hasSize(10)));

        mockMvc.perform(get("/api/v1/applications/A00001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.applicationId", is("A00001")))
                .andExpect(jsonPath("$.studentId", is("S1654")))
                .andExpect(jsonPath("$.companyId", is("C014")))
                .andExpect(jsonPath("$.jobId", is("J0263")))
                .andExpect(jsonPath("$.finalStatus", is(1)));

        mockMvc.perform(get("/api/v1/applications/NON_EXISTENT_APP"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.error", is("RESOURCE_NOT_FOUND")));
    }

    @Test
    void testAnalyticsTrends() throws Exception {
        mockMvc.perform(get("/api/v1/analytics/trends"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(4)))
                .andExpect(jsonPath("$[0].cycle", is(2023)))
                .andExpect(jsonPath("$[1].cycle", is(2024)))
                .andExpect(jsonPath("$[2].cycle", is(2025)))
                .andExpect(jsonPath("$[3].cycle", is(2026)));
    }

    @Test
    void testModelBenchmarks() throws Exception {
        mockMvc.perform(get("/api/v1/model/benchmarks"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)))
                .andExpect(jsonPath("$[0].modelName", notNullValue()));
    }
}
