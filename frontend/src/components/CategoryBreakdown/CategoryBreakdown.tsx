import { useState } from "react";
import type { CategoryResult } from "../../types/api";
import "./CategoryBreakdown.css";

interface Props {
  categories: CategoryResult[];
}

function barColor(score: number): string {
  if (score <= 3) return "#22c55e";
  if (score <= 6) return "#f59e0b";
  return "#ef4444";
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
        <span className="cat-score">{cat.raw_score}/10</span>
        <span className="cat-chevron">{expanded ? "▲" : "▼"}</span>
      </button>
      {expanded && cat.reasoning && (
        <p className="cat-reasoning">{cat.reasoning}</p>
      )}
    </div>
  );
}

export function CategoryBreakdown({ categories }: Props) {
  return (
    <div className="breakdown">
      <h3 className="breakdown-title">Category Breakdown</h3>
      {categories.map((cat) => (
        <CategoryRow key={cat.id} cat={cat} />
      ))}
    </div>
  );
}
