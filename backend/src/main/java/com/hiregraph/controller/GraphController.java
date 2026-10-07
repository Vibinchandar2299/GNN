package com.hiregraph.controller;

import com.hiregraph.dto.response.GraphOverviewResponse;
import com.hiregraph.dto.response.SubgraphResponse;
import com.hiregraph.service.GraphService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/graph")
public class GraphController {

    private final GraphService graphService;

    public GraphController(GraphService graphService) {
        this.graphService = graphService;
    }

    @GetMapping("/overview")
    public ResponseEntity<GraphOverviewResponse> getOverview() {
        return ResponseEntity.ok(graphService.getOverview());
    }

    @GetMapping("/subgraph/{type}/{id}")
    public ResponseEntity<SubgraphResponse> getSubgraph(
            @PathVariable String type,
            @PathVariable String id,
            @RequestParam(defaultValue = "50") int maxNeighbors) {
        return ResponseEntity.ok(graphService.getSubgraph(type, id, maxNeighbors));
    }
}
