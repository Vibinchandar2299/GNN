package com.hiregraph.service;

import com.hiregraph.client.AiServiceClient;
import com.hiregraph.dto.response.ModelBenchmarkResponse;
import com.hiregraph.dto.response.ModelMetadataResponse;
import com.hiregraph.mapper.EntityDtoMapper;
import com.hiregraph.repository.ModelBenchmarkRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;

@Service
@Transactional(readOnly = true)
public class ModelService {

    private final ModelBenchmarkRepository modelBenchmarkRepository;
    private final AiServiceClient aiServiceClient;

    public ModelService(ModelBenchmarkRepository modelBenchmarkRepository,
                        AiServiceClient aiServiceClient) {
        this.modelBenchmarkRepository = modelBenchmarkRepository;
        this.aiServiceClient = aiServiceClient;
    }

    public List<ModelBenchmarkResponse> getBenchmarks() {
        return modelBenchmarkRepository.findAll().stream()
                .map(EntityDtoMapper::toModelBenchmarkResponse)
                .toList();
    }

    @SuppressWarnings("unchecked")
    public ModelMetadataResponse getMetadata() {
        Map<String, Object> aiResult = aiServiceClient.getModelMetadata();

        ModelMetadataResponse resp = new ModelMetadataResponse();
        resp.setProjectName((String) aiResult.getOrDefault("project_name", "HireGraph AI"));
        resp.setResearchTitle((String) aiResult.getOrDefault("research_title", ""));
        resp.setModelName((String) aiResult.getOrDefault("model_name", "AMRG-GraphSAGE"));
        resp.setCheckpointFile((String) aiResult.getOrDefault("checkpoint_file", "AMRG_GraphSAGE_model.pt"));
        resp.setDevice((String) aiResult.getOrDefault("device", "CPU"));
        resp.setVerifiedResearchResults((Map<String, Object>) aiResult.get("verified_research_results"));
        resp.setGraphStatistics((Map<String, Object>) aiResult.get("graph_statistics"));
        resp.setTemporalSplit((Map<String, Object>) aiResult.get("temporal_split"));
        resp.setExplainability((Map<String, Object>) aiResult.get("explainability"));
        return resp;
    }
}
