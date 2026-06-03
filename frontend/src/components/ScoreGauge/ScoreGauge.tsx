import type { Verdict } from "../../types/api";
import "./ScoreGauge.css";

interface Props {
  score: number;
  verdict: Verdict;
}

const RADIUS = 70;
const STROKE = 14;
const CENTER = 90;
const CIRCUMFERENCE = Math.PI * RADIUS;

const VERDICT_CONFIG: Record<Verdict, { color: string; emoji: string }> = {
  "Probably Human": { color: "#16a34a", emoji: "✅" },
  "Uncertain":      { color: "#d97706", emoji: "🤔" },
  "Likely AI Slop": { color: "#ff4e00", emoji: "🤖" },
};

export function ScoreGauge({ score, verdict }: Props) {
  const { color, emoji } = VERDICT_CONFIG[verdict];
  const pct = score / 100;
  const dash = pct * CIRCUMFERENCE;
  const gap = CIRCUMFERENCE - dash;

  return (
    <div className="gauge-container">
      <svg width={CENTER * 2} height={CENTER + STROKE} viewBox={`0 0 ${CENTER * 2} ${CENTER + STROKE}`}>
        <path
          d={`M ${STROKE} ${CENTER} A ${RADIUS} ${RADIUS} 0 0 1 ${CENTER * 2 - STROKE} ${CENTER}`}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={STROKE}
          strokeLinecap="round"
        />
        <path
          d={`M ${STROKE} ${CENTER} A ${RADIUS} ${RADIUS} 0 0 1 ${CENTER * 2 - STROKE} ${CENTER}`}
          fill="none"
          stroke={color}
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={`${dash} ${gap}`}
          style={{ transition: "stroke-dasharray 0.7s cubic-bezier(0.34, 1.56, 0.64, 1)" }}
        />
      </svg>
      <div className="gauge-score" style={{ color }}>
        {score}<span className="gauge-out-of">/100</span>
      </div>
      <div className="gauge-label" style={{ color }}>
        {emoji} {verdict}
      </div>
    </div>
  );
}
