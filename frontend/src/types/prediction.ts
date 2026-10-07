export type PredictedStatus = 'SELECTED' | 'REJECTED';

export interface PredictionResponse {
  applicationId: string;
  predictedStatus: PredictedStatus | string;
  estimatedProbability: number;
  modelName: string;
  modelVersion: string;
  decisionSupportLabel: string;
  disclaimer: string;
}

export interface PredictionRequest {
  modelName?: string;
  modelVersion?: string;
  forceRefresh?: boolean;
}
