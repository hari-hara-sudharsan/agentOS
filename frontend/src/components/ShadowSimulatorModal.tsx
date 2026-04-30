
"use client";

import { useState } from "react";
import {
  AlertTriangle,
  CheckCircle,
  Shield,
  XCircle,
  ChevronDown,
  ChevronUp,
  Zap,
  Eye,
  Play,
  X,
  AlertOctagon,
  RefreshCw,
  ArrowRight,
  Info,
  Clock,
} from "lucide-react";

interface PredictedAction {
  action_name: string;
  description: string;
  probability: number;
  is_reversible: boolean;
  external_service: string | null;
}

interface IdentifiedRisk {
  risk_category: string;
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  mitigation: string | null;
}

interface SaferAlternative {
  action_name: string;
  description: string;
  risk_reduction: string;
  tradeoffs: string[];
}

interface ShadowSimulationData {
  simulation_id: string;
  tool_name: string;
  outcome: "success" | "caution" | "warning" | "blocked";
  predicted_actions: PredictedAction[];
  possible_risks: IdentifiedRisk[];
  safer_alternatives: SaferAlternative[];
  confidence_score: number;
  explanation: string;
  simulation_duration_ms: number;
}

interface ShadowSimulatorModalProps {
  data: ShadowSimulationData;
  onExecuteForReal: () => void;
  onCancel: () => void;
  loading?: boolean;
}

const OUTCOME_STYLES = {
  success: {
    bg: "bg-green-500/10",
    border: "border-green-500/30",
    text: "text-green-400",
    icon: CheckCircle,
    label: "Safe to Execute",
  },
  caution: {
    bg: "bg-yellow-500/10",
    border: "border-yellow-500/30",
    text: "text-yellow-400",
    icon: AlertTriangle,
    label: "Proceed with Caution",
  },
  warning: {
    bg: "bg-orange-500/10",
    border: "border-orange-500/30",
    text: "text-orange-400",
    icon: AlertOctagon,
    label: "Significant Risks Detected",
  },
  blocked: {
    bg: "bg-red-500/10",
    border: "border-red-500/30",
    text: "text-red-400",
    icon: XCircle,
    label: "Not Recommended",
  },
};

const SEVERITY_COLORS = {
  low: "text-green-400 bg-green-500/10 border-green-500/20",
  medium: "text-yellow-400 bg-yellow-500/10 border-yellow-500/20",
  high: "text-orange-400 bg-orange-500/10 border-orange-500/20",
  critical: "text-red-400 bg-red-500/10 border-red-500/20",
};

const RISK_CATEGORY_ICONS: Record<string, string> = {
  data_exposure: "🔓",
  unauthorized_access: "🚫",
  irreversible_action: "⚠️",
  scope_overreach: "📊",
  rate_limit: "⏱️",
  external_communication: "📤",
  financial_impact: "💰",
  privacy_violation: "👁️",
};

function ConfidenceBar({ score }: { score: number }) {
  const getColor = () => {
    if (score >= 80) return "bg-green-500";
    if (score >= 60) return "bg-yellow-500";
    if (score >= 40) return "bg-orange-500";
    return "bg-red-500";
  };

  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-zinc-500 uppercase tracking-wide">
        Confidence
      </span>
      <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
        <div
          className={`h-full ${getColor()} transition-all duration-500`}
          style={{ width: `${score}%` }}
        />
      </div>
      <span className="text-sm font-medium text-zinc-300">{score}%</span>
    </div>
  );
}

function PredictedActionsList({ actions }: { actions: PredictedAction[] }) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="space-y-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-sm font-medium text-zinc-300 hover:text-white transition-colors"
      >
        {expanded ? (
          <ChevronUp className="w-4 h-4" />
        ) : (
          <ChevronDown className="w-4 h-4" />
        )}
        <Play className="w-4 h-4 text-blue-400" />
        Predicted Actions ({actions.length})
      </button>

      {expanded && (
        <div className="space-y-2 ml-6">
          {actions.map((action, idx) => (
            <div
              key={idx}
              className="flex items-start gap-3 p-3 bg-zinc-800/50 rounded-lg border border-zinc-700"
            >
              <div className="flex-shrink-0 mt-0.5">
                <div
                  className={`w-2 h-2 rounded-full ${
                    action.probability >= 0.8
                      ? "bg-green-400"
                      : action.probability >= 0.5
                        ? "bg-yellow-400"
                        : "bg-zinc-500"
                  }`}
                />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-zinc-200">
                    {action.action_name}
                  </span>
                  {action.external_service && (
                    <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-400">
                      {action.external_service}
                    </span>
                  )}
                  {!action.is_reversible && (
                    <span className="text-xs px-2 py-0.5 rounded bg-red-500/20 text-red-400">
                      Irreversible
                    </span>
                  )}
                </div>
                <p className="text-xs text-zinc-400 mt-1">
                  {action.description}
                </p>
                <div className="text-xs text-zinc-500 mt-1">
                  Probability: {Math.round(action.probability * 100)}%
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function RisksList({ risks }: { risks: IdentifiedRisk[] }) {
  const [expanded, setExpanded] = useState(true);

  if (risks.length === 0) return null;

  const sortedRisks = [...risks].sort((a, b) => {
    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    return severityOrder[a.severity] - severityOrder[b.severity];
  });

  return (
    <div className="space-y-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-sm font-medium text-zinc-300 hover:text-white transition-colors"
      >
        {expanded ? (
          <ChevronUp className="w-4 h-4" />
        ) : (
          <ChevronDown className="w-4 h-4" />
        )}
        <Shield className="w-4 h-4 text-orange-400" />
        Identified Risks ({risks.length})
      </button>

      {expanded && (
        <div className="space-y-2 ml-6">
          {sortedRisks.map((risk, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-lg border ${SEVERITY_COLORS[risk.severity]}`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span>{RISK_CATEGORY_ICONS[risk.risk_category] || "⚠️"}</span>
                <span className="text-sm font-medium capitalize">
                  {risk.risk_category.replace(/_/g, " ")}
                </span>
                <span
                  className={`text-xs px-2 py-0.5 rounded uppercase font-bold ${
                    risk.severity === "critical"
                      ? "bg-red-500/30"
                      : risk.severity === "high"
                        ? "bg-orange-500/30"
                        : risk.severity === "medium"
                          ? "bg-yellow-500/30"
                          : "bg-green-500/30"
                  }`}
                >
                  {risk.severity}
                </span>
              </div>
              <p className="text-sm text-zinc-300">{risk.description}</p>
              {risk.mitigation && (
                <p className="text-xs text-zinc-400 mt-2 flex items-start gap-1">
                  <span className="text-green-400">💡</span>
                  <span>{risk.mitigation}</span>
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function AlternativesList({
  alternatives,
}: {
  alternatives: SaferAlternative[];
}) {
  const [expanded, setExpanded] = useState(false);

  if (alternatives.length === 0) return null;

  return (
    <div className="space-y-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-sm font-medium text-zinc-300 hover:text-white transition-colors"
      >
        {expanded ? (
          <ChevronUp className="w-4 h-4" />
        ) : (
          <ChevronDown className="w-4 h-4" />
        )}
        <RefreshCw className="w-4 h-4 text-purple-400" />
        Safer Alternatives ({alternatives.length})
      </button>

      {expanded && (
        <div className="space-y-2 ml-6">
          {alternatives.map((alt, idx) => (
            <div
              key={idx}
              className="p-3 bg-purple-500/10 rounded-lg border border-purple-500/30"
            >
              <div className="flex items-center gap-2 mb-1">
                <ArrowRight className="w-4 h-4 text-purple-400" />
                <span className="text-sm font-medium text-purple-300">
                  {alt.action_name}
                </span>
              </div>
              <p className="text-sm text-zinc-300">{alt.description}</p>
              <p className="text-xs text-green-400 mt-2">
                ✓ {alt.risk_reduction}
              </p>
              {alt.tradeoffs.length > 0 && (
                <div className="text-xs text-zinc-500 mt-1">
                  Tradeoffs: {alt.tradeoffs.join(", ")}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function ShadowSimulatorModal({
  data,
  onExecuteForReal,
  onCancel,
  loading,
}: ShadowSimulatorModalProps) {
  const outcomeStyle = OUTCOME_STYLES[data.outcome];
  const OutcomeIcon = outcomeStyle.icon;
  const hasHighRisks = data.possible_risks.some((r) =>
    ["high", "critical"].includes(r.severity),
  );

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-zinc-900 border border-zinc-700 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-900/50 via-purple-900/50 to-pink-900/50 px-6 py-4 border-b border-zinc-700 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-indigo-500/20 border border-indigo-500/30">
                <Eye className="w-5 h-5 text-indigo-400" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">
                  What-If Preview
                </h2>
                <p className="text-sm text-zinc-400">
                  Shadow Simulator Analysis
                </p>
              </div>
            </div>
            <button
              onClick={onCancel}
              className="p-2 rounded-lg hover:bg-zinc-800 transition-colors"
            >
              <X className="w-5 h-5 text-zinc-400" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {/* Tool & Outcome Badge */}
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-400" />
              <span className="text-lg font-medium text-white">
                {data.tool_name}
              </span>
            </div>
            <div
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${outcomeStyle.bg} ${outcomeStyle.border}`}
            >
              <OutcomeIcon className={`w-4 h-4 ${outcomeStyle.text}`} />
              <span className={`text-sm font-medium ${outcomeStyle.text}`}>
                {outcomeStyle.label}
              </span>
            </div>
          </div>

          {/* Confidence Bar */}
          <ConfidenceBar score={data.confidence_score} />

          {/* Explanation */}
          <div className="p-4 bg-zinc-800/50 rounded-lg border border-zinc-700">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-zinc-300 leading-relaxed">
                {data.explanation}
              </p>
            </div>
          </div>

          {/* Simulation Duration */}
          <div className="flex items-center gap-2 text-xs text-zinc-500">
            <Clock className="w-3 h-3" />
            <span>Simulation completed in {data.simulation_duration_ms}ms</span>
            <span className="text-zinc-600">•</span>
            <span>ID: {data.simulation_id}</span>
          </div>

          {/* Predicted Actions */}
          <PredictedActionsList actions={data.predicted_actions} />

          {/* Risks */}
          <RisksList risks={data.possible_risks} />

          {/* Safer Alternatives */}
          <AlternativesList alternatives={data.safer_alternatives} />
        </div>

        {/* Actions */}
        <div className="px-6 py-4 bg-zinc-800/50 border-t border-zinc-700 flex gap-3 flex-shrink-0">
          <button
            onClick={onCancel}
            disabled={loading}
            className="flex-1 px-4 py-2.5 rounded-lg border border-zinc-600 text-zinc-300 hover:bg-zinc-700 hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            onClick={onExecuteForReal}
            disabled={loading || data.outcome === "blocked"}
            className={`flex-1 px-4 py-2.5 rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 ${
              hasHighRisks
                ? "bg-gradient-to-r from-orange-600 to-red-600 text-white hover:from-orange-500 hover:to-red-500"
                : "bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:from-green-500 hover:to-emerald-500"
            }`}
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Executing...
              </>
            ) : data.outcome === "blocked" ? (
              <>
                <XCircle className="w-4 h-4" />
                Execution Blocked
              </>
            ) : hasHighRisks ? (
              <>
                <AlertTriangle className="w-4 h-4" />
                Execute Anyway (Risky)
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Execute for Real
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
