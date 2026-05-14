import type { AnalysisResult } from "../../types/api";
import { ScoreGauge } from "../ScoreGauge/ScoreGauge";
import { CategoryBreakdown } from "../CategoryBreakdown/CategoryBreakdown";
import "./ResultCard.css";

interface Props {
  result: AnalysisResult;
}

export function ResultCard({ result }: Props) {
  return (
    <div className="result-card">
      <div className="result-top">
        <ScoreGauge score={result.score} verdict={result.verdict} />
        {result.source_url && (
          <a className="result-url" href={result.source_url} target="_blank" rel="noreferrer">
            {result.source_url}
          </a>
        )}
      </div>
      <CategoryBreakdown categories={result.categories} />
      <p className="result-meta">
        {result.model} · rubric v{result.rubric_version} · {result.analysis_ms}ms
      </p>
    </div>
  );
}
