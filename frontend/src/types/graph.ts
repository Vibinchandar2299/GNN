export interface GraphOverview {
  totalNodes: number;
  totalEdges: number;
  relationTypesCount: number;
  featureDimension: number;
  nodeCountsByType: Record<string, number>;
  relationTypes: string[];
}

export interface GraphNode {
  id: string;
  node_index?: number;
  type: string;
  is_center?: boolean;
}

export interface GraphLink {
  source: string;
  source_type?: string;
  target: string;
  target_type?: string;
  relation: string;
  relation_id?: number;
}

export interface SubgraphResponse {
  centerNode: {
    id: string;
    type: string;
    node_index?: number;
  };
  nodesCount: number;
  linksCount: number;
  nodes: GraphNode[];
  links: GraphLink[];
}
