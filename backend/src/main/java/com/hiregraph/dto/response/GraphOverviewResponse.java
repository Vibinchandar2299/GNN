package com.hiregraph.dto.response;

import java.util.List;
import java.util.Map;

public class GraphOverviewResponse {
    private int totalNodes;
    private int totalEdges;
    private int relationTypesCount;
    private int featureDimension;
    private Map<String, Integer> nodeCountsByType;
    private List<String> relationTypes;

    public GraphOverviewResponse() {}

    public GraphOverviewResponse(int totalNodes, int totalEdges, int relationTypesCount,
                                 int featureDimension, Map<String, Integer> nodeCountsByType,
                                 List<String> relationTypes) {
        this.totalNodes = totalNodes;
        this.totalEdges = totalEdges;
        this.relationTypesCount = relationTypesCount;
        this.featureDimension = featureDimension;
        this.nodeCountsByType = nodeCountsByType;
        this.relationTypes = relationTypes;
    }

    public int getTotalNodes() { return totalNodes; }
    public void setTotalNodes(int totalNodes) { this.totalNodes = totalNodes; }

    public int getTotalEdges() { return totalEdges; }
    public void setTotalEdges(int totalEdges) { this.totalEdges = totalEdges; }

    public int getRelationTypesCount() { return relationTypesCount; }
    public void setRelationTypesCount(int relationTypesCount) { this.relationTypesCount = relationTypesCount; }

    public int getFeatureDimension() { return featureDimension; }
    public void setFeatureDimension(int featureDimension) { this.featureDimension = featureDimension; }

    public Map<String, Integer> getNodeCountsByType() { return nodeCountsByType; }
    public void setNodeCountsByType(Map<String, Integer> nodeCountsByType) { this.nodeCountsByType = nodeCountsByType; }

    public List<String> getRelationTypes() { return relationTypes; }
    public void setRelationTypes(List<String> relationTypes) { this.relationTypes = relationTypes; }
}
