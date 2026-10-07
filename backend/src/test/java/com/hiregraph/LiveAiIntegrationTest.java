package com.hiregraph;

import com.hiregraph.dto.response.ModelMetadataResponse;
import com.hiregraph.dto.response.PredictionResponse;
import com.hiregraph.dto.response.SubgraphResponse;
import com.hiregraph.entity.Prediction;
import com.hiregraph.enums.PredictedStatus;
import com.hiregraph.repository.PredictionRepository;
import com.hiregraph.service.DataIngestionService;
import com.hiregraph.service.GraphService;
import com.hiregraph.service.ModelService;
import com.hiregraph.service.PredictionService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.within;

@SpringBootTest(properties = {
        "hiregraph.ai-service.base-url=http://localhost:8000"
})
public class LiveAiIntegrationTest {

    @Autowired
    private PredictionService predictionService;

    @Autowired
    private PredictionRepository predictionRepository;

    @Autowired
    private GraphService graphService;

    @Autowired
    private ModelService modelService;

    @Autowired
    private DataIngestionService ingestionService;

    @BeforeEach
    void setup() {
        ingestionService.ingestData(false);
        predictionRepository.deleteAll();
    }

    @Test
    @DisplayName("Verify live prediction accuracy for A00001, A00002, A00003, A00004 against Phase 1 golden values")
    void testLivePredictionsParity() {
        // Record 1: A00001 -> 0.8063023686408997, SELECTED
        PredictionResponse p1 = predictionService.predictApplication("A00001");
        assertThat(p1.getApplicationId()).isEqualTo("A00001");
        assertThat(p1.getPredictedStatus()).isEqualTo(PredictedStatus.SELECTED.name());
        assertThat(p1.getEstimatedProbability()).isCloseTo(0.8063023686408997, within(1e-6));
        assertThat(p1.getModelName()).isEqualTo("AMRG-GraphSAGE");
        assertThat(p1.getModelVersion()).isEqualTo("research-v1");

        // Record 2: A00002 -> 0.13230180740356445, REJECTED
        PredictionResponse p2 = predictionService.predictApplication("A00002");
        assertThat(p2.getApplicationId()).isEqualTo("A00002");
        assertThat(p2.getPredictedStatus()).isEqualTo(PredictedStatus.REJECTED.name());
        assertThat(p2.getEstimatedProbability()).isCloseTo(0.13230180740356445, within(1e-6));

        // Record 3: A00003 -> 0.16538043320178986, REJECTED
        PredictionResponse p3 = predictionService.predictApplication("A00003");
        assertThat(p3.getApplicationId()).isEqualTo("A00003");
        assertThat(p3.getPredictedStatus()).isEqualTo(PredictedStatus.REJECTED.name());
        assertThat(p3.getEstimatedProbability()).isCloseTo(0.16538043320178986, within(1e-6));

        // Record 4: A00004 -> 0.8380703330039978, SELECTED
        PredictionResponse p4 = predictionService.predictApplication("A00004");
        assertThat(p4.getApplicationId()).isEqualTo("A00004");
        assertThat(p4.getPredictedStatus()).isEqualTo(PredictedStatus.SELECTED.name());
        assertThat(p4.getEstimatedProbability()).isCloseTo(0.8380703330039978, within(1e-6));

        // Verify DB persistence
        List<Prediction> allPredictions = predictionRepository.findAll();
        assertThat(allPredictions).hasSize(4);

        // Verify persistence & caching (no duplicates created on second call)
        PredictionResponse p1Cached = predictionService.predictApplication("A00001");
        assertThat(p1Cached.getEstimatedProbability()).isEqualTo(p1.getEstimatedProbability());
        assertThat(predictionRepository.findAll()).hasSize(4);
    }

    @Test
    @DisplayName("Verify live model metadata retrieval from FastAPI")
    void testLiveModelMetadata() {
        ModelMetadataResponse metadata = modelService.getMetadata();
        assertThat(metadata.getModelName()).isEqualTo("AMRG-GraphSAGE");
        Map<String, Object> stats = metadata.getGraphStatistics();
        assertThat(stats).isNotNull();
        assertThat(((Number) stats.get("total_nodes")).intValue()).isEqualTo(5977);
        assertThat(((Number) stats.get("total_edges")).intValue()).isEqualTo(43044);
        assertThat(((Number) stats.get("relation_types_count")).intValue()).isEqualTo(12);
        assertThat(((Number) stats.get("feature_dimension")).intValue()).isEqualTo(82);
    }

    @Test
    @DisplayName("Verify live graph subgraph / neighborhood retrieval from FastAPI")
    void testLiveGraphNeighborhood() {
        SubgraphResponse response = graphService.getSubgraph("application", "A00001", 10);
        assertThat(response).isNotNull();
        assertThat(response.getCenterNode()).isNotNull();
        assertThat(response.getCenterNode().get("id")).isEqualTo("A00001");
        assertThat(response.getNodes()).isNotEmpty();
        assertThat(response.getLinks()).isNotEmpty();
    }
}
