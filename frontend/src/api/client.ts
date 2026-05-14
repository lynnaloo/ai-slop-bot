import type { AnalysisResult, AnalyzeFormData } from "../types/api";

export async function analyzeContent(data: AnalyzeFormData): Promise<AnalysisResult> {
  const form = new FormData();
  form.append("input_type", data.input_type);
  if (data.url) form.append("url", data.url);
  if (data.text) form.append("text", data.text);
  if (data.image) form.append("image", data.image);

  const res = await fetch("/api/analyze", { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Analysis failed");
  }
  return res.json();
}
