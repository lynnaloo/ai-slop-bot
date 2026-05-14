import type { Verdict } from "../../types/api";
import "./ScoreGauge.css";

interface Props {
  score: number;
  verdict: Verdict;
}

const RADIUS = 70;
const STROKE = 12;
const CENTER = 90;
const CIRCUMFERENCE = Math.PI * RADIUS; // half-circle

function scoreColor(score: number): string {
  if (score <= 30) return "#22c55e";
  if (score <= 60) return "#f59e0b";
  return "#ef4444";
}

export function ScoreGauge({ score, verdict }: Props) {
  const pct = score / 100;
  const dash = pct * CIRCUMFERENCE;
  const gap = CIRCUMFERENCE - dash;
  const color = scoreColor(score);

  return (
    <div className="gauge-container">
      <svg width={CENTER * 2} height={CENTER + STROKE} viewBox={`0 0 ${CENTER * 2} ${CENTER + STROKE}`}>
        {/* Track */}
        <path
          d={`M ${STROKE} ${CENTER} A ${RADIUS} ${RADIUS} 0 0 1 ${CENTER * 2 - STROKE} ${CENTER}`}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={STROKE}
          strokeLinecap="round"
        />
        {/* Fill */}
        <path
          d={`M ${STROKE} ${CENTER} A ${RADIUS} ${RADIUS} 0 0 1 ${CENTER * 2 - STROKE} ${CENTER}`}
          fill="none"
          stroke={color}
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={`${dash} ${gap}`}
          style={{ transition: "stroke-dasharray 0.6s ease" }}
        />
      </svg>
      <div className="gauge-score" style={{ color }}>
        {score}
      </div>
      <div className="gauge-label">{verdict}</div>
    </div>
  );
}
