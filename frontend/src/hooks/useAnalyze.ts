import { useMutation } from "@tanstack/react-query";
import { analyzeContent } from "../api/client";
import type { AnalyzeFormData, AnalysisResult } from "../types/api";

export function useAnalyze() {
  return useMutation<AnalysisResult, Error, AnalyzeFormData>({
    mutationFn: analyzeContent,
  });
}
