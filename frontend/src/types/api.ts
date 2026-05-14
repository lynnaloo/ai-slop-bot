export type InputType = "url" | "image" | "text";

export type Verdict = "Probably Human" | "Uncertain" | "Likely AI Slop";

export interface CategoryResult {
  id: string;
  label: string;
  raw_score: number;
  weighted_score: number;
  weight: number;
  reasoning: string;
}

export interface AnalysisResult {
  score: number;
  verdict: Verdict;
  categories: CategoryResult[];
  input_type: InputType;
  source_url: string | null;
  rubric_version: string;
  model: string;
  analysis_ms: number;
}

export interface AnalyzeFormData {
  input_type: InputType;
  url?: string;
  text?: string;
  image?: File;
}
