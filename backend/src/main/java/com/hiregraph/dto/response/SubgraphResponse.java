package com.hiregraph.dto.response;

import java.util.List;
import java.util.Map;

public class SubgraphResponse {
    private Map<String, Object> centerNode;
    private int nodesCount;
    private int linksCount;
    private List<Map<String, Object>> nodes;
    private List<Map<String, Object>> links;

    public SubgraphResponse() {}

    public SubgraphResponse(Map<String, Object> centerNode, int nodesCount, int linksCount,
                            List<Map<String, Object>> nodes, List<Map<String, Object>> links) {
        this.centerNode = centerNode;
        this.nodesCount = nodesCount;
        this.linksCount = linksCount;
        this.nodes = nodes;
        this.links = links;
    }

    public Map<String, Object> getCenterNode() { return centerNode; }
    public void setCenterNode(Map<String, Object> centerNode) { this.centerNode = centerNode; }

    public int getNodesCount() { return nodesCount; }
    public void setNodesCount(int nodesCount) { this.nodesCount = nodesCount; }

    public int getLinksCount() { return linksCount; }
    public void setLinksCount(int linksCount) { this.linksCount = linksCount; }

    public List<Map<String, Object>> getNodes() { return nodes; }
    public void setNodes(List<Map<String, Object>> nodes) { this.nodes = nodes; }

    public List<Map<String, Object>> getLinks() { return links; }
    public void setLinks(List<Map<String, Object>> links) { this.links = links; }
}
