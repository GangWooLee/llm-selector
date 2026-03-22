export interface ModelSummary {
  id: string;
  openrouter_id: string;
  name: string;
  provider: string;
  context_length: number;
  pricing_input: number;
  pricing_output: number;
  is_free: boolean;
  modalities: string[];
  supported_parameters: string[];
}

export interface Benchmark {
  benchmark_name: string;
  score: number;
  max_score: number;
  source_url?: string;
}

export interface Tag {
  category: string;
  strength_level: number;
}

export interface ModelDetail extends ModelSummary {
  description: string;
  max_completion_tokens: number | null;
  architecture: Record<string, string> | null;
  benchmarks: Benchmark[];
  tags: Tag[];
  updated_at: string;
}

export interface MonthlyCost {
  low: number;
  medium: number;
  high: number;
}

export interface TopPick {
  model_id: string;
  model_name: string;
  reason: string;
}

export interface ModelRecommendation {
  model_id: string;
  model_name: string;
  provider: string;
  overall_score: number;
  price_score: number;
  performance_score: number;
  fit_score: number;
  strengths: string[];
  weaknesses: string[];
  monthly_cost_estimate: MonthlyCost;
  best_for: string;
}

export interface AgentStep {
  step_number: number;
  action: string;
  reasoning: string;
  result_summary: string;
}

export interface ComparisonReport {
  top_recommendation: TopPick;
  recommendations: ModelRecommendation[];
  summary: string;
  data_sources: string[];
  agent_reasoning: AgentStep[];
}
