package com.hiregraph.service;

import com.hiregraph.client.AiServiceClient;
import com.hiregraph.dto.response.GraphOverviewResponse;
import com.hiregraph.dto.response.SubgraphResponse;
import com.hiregraph.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

@Service
@Transactional(readOnly = true)
public class GraphService {

    private final AiServiceClient aiServiceClient;
    private final StudentRepository studentRepository;
    private final CompanyRepository companyRepository;
    private final JobRepository jobRepository;
    private final SkillRepository skillRepository;
    private final ApplicationRepository applicationRepository;

    public GraphService(AiServiceClient aiServiceClient,
                        StudentRepository studentRepository,
                        CompanyRepository companyRepository,
                        JobRepository jobRepository,
                        SkillRepository skillRepository,
                        ApplicationRepository applicationRepository) {
        this.aiServiceClient = aiServiceClient;
        this.studentRepository = studentRepository;
        this.companyRepository = companyRepository;
        this.jobRepository = jobRepository;
        this.skillRepository = skillRepository;
        this.applicationRepository = applicationRepository;
    }

    public GraphOverviewResponse getOverview() {
        Map<String, Integer> nodeCounts = new LinkedHashMap<>();
        nodeCounts.put("application", (int) applicationRepository.count());
        nodeCounts.put("student", (int) studentRepository.count());
        nodeCounts.put("company", (int) companyRepository.count());
        nodeCounts.put("job", (int) jobRepository.count());
        nodeCounts.put("skill", (int) skillRepository.count());

        List<String> relations = List.of(
                "APPLICATION_STUDENT", "STUDENT_APPLICATION",
                "APPLICATION_COMPANY", "COMPANY_APPLICATION",
                "APPLICATION_JOB", "JOB_APPLICATION",
                "HAS_SKILL", "REV_HAS_SKILL",
                "REQUIRES_SKILL", "REV_REQUIRES_SKILL",
                "OFFERED_BY", "REV_OFFERED_BY"
        );

        int totalNodes = nodeCounts.values().stream().mapToInt(Integer::intValue).sum();
        int totalEdges = 43044; // Total multi-relational edges in frozen PyG graph

        return new GraphOverviewResponse(
                totalNodes,
                totalEdges,
                relations.size(),
                82,
                nodeCounts,
                relations
        );
    }

    @SuppressWarnings("unchecked")
    public SubgraphResponse getSubgraph(String type, String id, int maxNeighbors) {
        Map<String, Object> aiResult = aiServiceClient.getNeighborhood(type, id, maxNeighbors);

        Map<String, Object> centerNode = (Map<String, Object>) aiResult.get("center_node");
        int nodesCount = ((Number) aiResult.getOrDefault("nodes_count", 0)).intValue();
        int linksCount = ((Number) aiResult.getOrDefault("links_count", 0)).intValue();
        List<Map<String, Object>> nodes = (List<Map<String, Object>>) aiResult.getOrDefault("nodes", Collections.emptyList());
        List<Map<String, Object>> links = (List<Map<String, Object>>) aiResult.getOrDefault("links", Collections.emptyList());

        return new SubgraphResponse(centerNode, nodesCount, linksCount, nodes, links);
    }
}
