import { useState } from "react";
import type { CategoryResult } from "../../types/api";
import "./CategoryBreakdown.css";

interface Props {
  categories: CategoryResult[];
}

function barColor(score: number): string {
  if (score <= 3) return "#16a34a";
  if (score <= 6) return "#d97706";
  return "#ff4e00";
}

function CategoryRow({ cat }: { cat: CategoryResult }) {
  const [expanded, setExpanded] = useState(false);
  const pct = (cat.raw_score / 10) * 100;

  return (
    <div className="cat-row">
      <button className="cat-header" onClick={() => setExpanded((v) => !v)} aria-expanded={expanded}>
        <span className="cat-label">{cat.label}</span>
        <div className="cat-bar-wrap">
          <div
            className="cat-bar"
            style={{ width: `${pct}%`, background: barColor(cat.raw_score) }}
          />
        </div>
        <span className="cat-score" style={{ color: barColor(cat.raw_score) }}>
          {cat.raw_score}/10
        </span>
        <span className="cat-chevron">{expanded ? "▲" : "▼"}</span>
      </button>
      {expanded && cat.reasoning && (
        <p className="cat-reasoning">{cat.reasoning}</p>
      )}
    </div>
  );
}

const TIER1_IDS = new Set(["iteration_absence", "real_problem_solved", "voiceless_decisions"]);

export function CategoryBreakdown({ categories }: Props) {
  const tier1 = categories.filter((c) => TIER1_IDS.has(c.id));
  const tier2 = categories.filter((c) => !TIER1_IDS.has(c.id));

  return (
    <div className="breakdown">
      <p className="breakdown-title">Category Breakdown</p>

      {tier1.length > 0 && (
        <div className="breakdown-group">
          <span className="breakdown-group-label breakdown-group-label--tier1">
            ✨ Polished but Hollow
          </span>
          {tier1.map((cat) => <CategoryRow key={cat.id} cat={cat} />)}
        </div>
      )}

      {tier2.length > 0 && (
        <div className="breakdown-group">
          <span className="breakdown-group-label breakdown-group-label--tier2">
            💀 Generated & Abandoned
          </span>
          {tier2.map((cat) => <CategoryRow key={cat.id} cat={cat} />)}
        </div>
      )}
    </div>
  );
}
