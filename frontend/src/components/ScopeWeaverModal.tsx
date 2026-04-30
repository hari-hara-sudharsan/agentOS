"use client";

import { useState } from "react";
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  Zap,
  Lock,
  Unlock,
  Info,
} from "lucide-react";

interface ScopeWeaverData {
  approval_id: string;
  tool: string;
  binding_message: string;
  original_scopes: string[];
  recommended_scopes: string[];
  scope_evolution_score: number;
  risk_level: "low" | "medium" | "high" | "critical";
  ai_explanation: string;
  params?: Record<string, unknown>;
}

interface ScopeWeaverModalProps {
  data: ScopeWeaverData;
  onApprove: (approvalId: string) => void;
  onDeny: (approvalId: string) => void;
  loading?: boolean;
}

const RISK_COLORS = {
  low: {
    bg: "bg-green-500/20",
    border: "border-green-500/50",
    text: "text-green-400",
    icon: CheckCircle,
  },
  medium: {
    bg: "bg-yellow-500/20",
    border: "border-yellow-500/50",
    text: "text-yellow-400",
    icon: AlertTriangle,
  },
  high: {
    bg: "bg-orange-500/20",
    border: "border-orange-500/50",
    text: "text-orange-400",
    icon: AlertTriangle,
  },
  critical: {
    bg: "bg-red-500/20",
    border: "border-red-500/50",
    text: "text-red-400",
    icon: Shield,
  },
};

const SCOPE_DESCRIPTIONS: Record<string, string> = {
  // Gmail scopes
  "https://www.googleapis.com/auth/gmail.readonly": "Read all emails",
  "https://www.googleapis.com/auth/gmail.send": "Send emails only",
  "https://www.googleapis.com/auth/gmail.compose": "Create draft emails",
  "https://www.googleapis.com/auth/gmail.modify": "Read, send, delete emails",
  "https://mail.google.com/": "Full mailbox access",
  // Calendar scopes
  "https://www.googleapis.com/auth/calendar": "Full calendar access",
  "https://www.googleapis.com/auth/calendar.readonly": "Read calendar only",
  "https://www.googleapis.com/auth/calendar.events": "Manage events",
  "https://www.googleapis.com/auth/calendar.events.readonly":
    "Read events only",
  // Drive scopes
  "https://www.googleapis.com/auth/drive": "Full Drive access",
  "https://www.googleapis.com/auth/drive.readonly": "Read files only",
  "https://www.googleapis.com/auth/drive.file": "Access files created by app",
  "https://www.googleapis.com/auth/drive.metadata.readonly":
    "View file metadata",
  // GitHub scopes
  repo: "Full repository access",
  "repo:status": "Repository status only",
  public_repo: "Public repos only",
  "read:user": "Read user profile",
  "user:email": "Access email address",
};

function getScopeLabel(scope: string): string {
  return SCOPE_DESCRIPTIONS[scope] || scope.split("/").pop() || scope;
}

function ScopeComparison({
  original,
  recommended,
}: {
  original: string[];
  recommended: string[];
}) {
  const [expanded, setExpanded] = useState(false);
  const removedScopes = original.filter((s) => !recommended.includes(s));
  const keptScopes = original.filter((s) => recommended.includes(s));

  return (
    <div className="space-y-3">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-200 transition-colors"
      >
        {expanded ? (
          <ChevronUp className="w-4 h-4" />
        ) : (
          <ChevronDown className="w-4 h-4" />
        )}
        <span>
          View scope details ({recommended.length} of {original.length} scopes)
        </span>
      </button>

      {expanded && (
        <div className="grid grid-cols-2 gap-4 mt-2">
          <div className="space-y-2">
            <div className="text-xs font-medium text-zinc-500 uppercase tracking-wide">
              Original Request
            </div>
            <div className="space-y-1">
              {original.map((scope) => {
                const isRemoved = removedScopes.includes(scope);
                return (
                  <div
                    key={scope}
                    className={`flex items-center gap-2 text-xs px-2 py-1 rounded ${
                      isRemoved
                        ? "bg-red-500/10 text-red-400 line-through"
                        : "bg-zinc-800/50 text-zinc-300"
                    }`}
                  >
                    {isRemoved ? (
                      <Unlock className="w-3 h-3 flex-shrink-0" />
                    ) : (
                      <Lock className="w-3 h-3 flex-shrink-0" />
                    )}
                    <span className="truncate" title={scope}>
                      {getScopeLabel(scope)}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="space-y-2">
            <div className="text-xs font-medium text-zinc-500 uppercase tracking-wide">
              Recommended (Minimal)
            </div>
            <div className="space-y-1">
              {recommended.map((scope) => (
                <div
                  key={scope}
                  className="flex items-center gap-2 text-xs px-2 py-1 rounded bg-green-500/10 text-green-400"
                >
                  <CheckCircle className="w-3 h-3 flex-shrink-0" />
                  <span className="truncate" title={scope}>
                    {getScopeLabel(scope)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function EvolutionScore({ score }: { score: number }) {
  const getColor = () => {
    if (score >= 75) return "text-green-400";
    if (score >= 50) return "text-yellow-400";
    if (score >= 25) return "text-orange-400";
    return "text-zinc-400";
  };

  const getLabel = () => {
    if (score >= 75) return "Excellent";
    if (score >= 50) return "Good";
    if (score >= 25) return "Moderate";
    return "Minimal";
  };

  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
        <div
          className={`h-full ${score >= 75 ? "bg-green-500" : score >= 50 ? "bg-yellow-500" : score >= 25 ? "bg-orange-500" : "bg-zinc-600"} transition-all duration-500`}
          style={{ width: `${score}%` }}
        />
      </div>
      <div className={`text-sm font-medium ${getColor()}`}>
        {score}% {getLabel()}
      </div>
    </div>
  );
}

export default function ScopeWeaverModal({
  data,
  onApprove,
  onDeny,
  loading,
}: ScopeWeaverModalProps) {
  const riskStyle = RISK_COLORS[data.risk_level] || RISK_COLORS.medium;
  const RiskIcon = riskStyle.icon;
  const scopeReduction =
    data.original_scopes.length - data.recommended_scopes.length;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-zinc-900 border border-zinc-700 rounded-xl max-w-lg w-full shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 px-6 py-4 border-b border-zinc-700">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-500/20 border border-purple-500/30">
              <Zap className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">
                Scope Weaver Recommendation
              </h2>
              <p className="text-sm text-zinc-400">
                AI-optimized permissions for this action
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5">
          {/* Tool & Action */}
          <div className="flex items-start gap-3 p-3 bg-zinc-800/50 rounded-lg border border-zinc-700">
            <Info className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-sm font-medium text-zinc-200">
                {data.tool}
              </div>
              <div className="text-sm text-zinc-400 mt-1">
                {data.binding_message}
              </div>
            </div>
          </div>

          {/* Risk Level */}
          <div
            className={`flex items-center gap-3 p-3 rounded-lg border ${riskStyle.bg} ${riskStyle.border}`}
          >
            <RiskIcon className={`w-5 h-5 ${riskStyle.text}`} />
            <div className="flex-1">
              <div
                className={`text-sm font-medium ${riskStyle.text} capitalize`}
              >
                {data.risk_level} Risk Action
              </div>
            </div>
            {scopeReduction > 0 && (
              <div className="px-2 py-1 rounded bg-green-500/20 text-green-400 text-xs font-medium">
                -{scopeReduction} scopes
              </div>
            )}
          </div>

          {/* AI Explanation */}
          <div className="space-y-2">
            <div className="text-sm font-medium text-zinc-300">
              OpenClaw Analysis
            </div>
            <div className="text-sm text-zinc-400 leading-relaxed bg-zinc-800/30 rounded-lg p-3 border border-zinc-800">
              {data.ai_explanation}
            </div>
          </div>

          {/* Scope Evolution Score */}
          <div className="space-y-2">
            <div className="text-sm font-medium text-zinc-300">
              Scope Evolution Score
            </div>
            <EvolutionScore score={data.scope_evolution_score} />
            <div className="text-xs text-zinc-500">
              Higher score = more permissions removed while maintaining
              functionality
            </div>
          </div>

          {/* Scope Comparison */}
          <ScopeComparison
            original={data.original_scopes}
            recommended={data.recommended_scopes}
          />
        </div>

        {/* Actions */}
        <div className="px-6 py-4 bg-zinc-800/50 border-t border-zinc-700 flex gap-3">
          <button
            onClick={() => onDeny(data.approval_id)}
            disabled={loading}
            className="flex-1 px-4 py-2.5 rounded-lg border border-zinc-600 text-zinc-300 hover:bg-zinc-700 hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Deny
          </button>
          <button
            onClick={() => onApprove(data.approval_id)}
            disabled={loading}
            className="flex-1 px-4 py-2.5 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 text-white font-medium hover:from-purple-500 hover:to-blue-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <CheckCircle className="w-4 h-4" />
                Approve with Minimal Scopes
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
