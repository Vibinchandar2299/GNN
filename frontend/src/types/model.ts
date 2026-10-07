export interface ModelBenchmark {
  modelName: string;
  accuracy: number;
  precisionScore: number;
  recall: number;
  f1Score: number;
  rocAuc: number;
  datasetDescription: string;
}

export interface ModelMetadata {
  projectName: string;
  researchTitle: string;
  modelName: string;
  checkpointFile: string;
  device: string;
  verifiedResearchResults?: {
    Standard_GraphSAGE?: {
      accuracy: number;
      precision: number;
      recall: number;
      f1: number;
      roc_auc: number;
    };
    AMRG_GraphSAGE?: {
      accuracy: number;
      precision: number;
      recall: number;
      f1: number;
      roc_auc: number;
    };
  };
  graphStatistics?: {
    total_nodes: number;
    application_nodes: number;
    student_nodes: number;
    company_nodes: number;
    job_nodes: number;
    skill_nodes: number;
    total_edges: number;
    relation_types_count: number;
    feature_dimension: number;
  };
  temporalSplit?: {
    training_cycles: number[];
    validation_cycle: number[];
    test_cycle: number[];
  };
  explainability?: {
    gnnexplainer_active: boolean;
    status_note: string;
  };
}
