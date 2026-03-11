"use client";

import { useEffect, useState, useCallback } from "react";
import { History, ChevronLeft, ChevronRight, Brain } from "lucide-react";
import { getDiagnosisHistory } from "@/lib/api";

interface HistoryRecord {
  id: string;
  age: number;
  gender: string;
  symptoms: string[];
  diagnosis: string;
  confidence: number;
  ai_suggestion?: string;
  root_cause?: string;
  created_at: string;
}

export default function HistoryPage() {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getDiagnosisHistory({ page, limit: 15 });
      setRecords(res.data.history);
      setTotal(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    load();
  }, [load]);

  const pages = Math.ceil(total / 15);

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-text-primary">Diagnosis History</h1>
        <p className="text-text-secondary mt-1">
          {total} diagnosis records
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <div className="w-8 h-8 border-3 border-accent-teal/30 border-t-accent-teal rounded-full animate-spin" />
        </div>
      ) : records.length === 0 ? (
        <div className="rounded-2xl bg-bg-card border border-border p-12 text-center">
          <History className="w-12 h-12 text-text-muted mx-auto mb-3" />
          <p className="text-text-secondary">No diagnosis history yet</p>
          <p className="text-text-muted text-sm mt-1">
            Run a diagnosis to see it here
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {records.map((r) => (
            <div
              key={r.id}
              className="rounded-2xl bg-bg-card border border-border overflow-hidden transition-all"
            >
              <div
                className="p-5 flex items-center justify-between cursor-pointer hover:bg-bg-card-hover transition"
                onClick={() =>
                  setExpanded(expanded === r.id ? null : r.id)
                }
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-accent-teal/15 flex items-center justify-center">
                    <Brain className="w-5 h-5 text-accent-teal" />
                  </div>
                  <div>
                    <p className="font-medium text-text-primary">
                      {r.diagnosis}
                    </p>
                    <p className="text-xs text-text-muted">
                      {r.age}y {r.gender} &middot;{" "}
                      {new Date(r.created_at).toLocaleDateString("en-IN", {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <div className="w-20 h-2 rounded-full bg-bg-primary overflow-hidden">
                      <div
                        className="h-full rounded-full bg-accent-teal"
                        style={{ width: `${r.confidence}%` }}
                      />
                    </div>
                    <span className="text-sm font-bold text-accent-teal">
                      {r.confidence}%
                    </span>
                  </div>
                </div>
              </div>

              {expanded === r.id && (
                <div className="px-5 pb-5 border-t border-border/50 pt-4 space-y-3">
                  <div>
                    <p className="text-xs font-semibold text-text-muted uppercase mb-1">
                      Symptoms
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {r.symptoms?.map((s, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded bg-accent-teal/10 text-accent-teal text-xs"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                  {r.ai_suggestion && (
                    <div>
                      <p className="text-xs font-semibold text-text-muted uppercase mb-1">
                        AI Assessment
                      </p>
                      <p className="text-sm text-text-secondary">
                        {r.ai_suggestion}
                      </p>
                    </div>
                  )}
                  {r.root_cause && (
                    <div>
                      <p className="text-xs font-semibold text-text-muted uppercase mb-1">
                        Root Cause
                      </p>
                      <p className="text-sm text-text-secondary">
                        {r.root_cause}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {pages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-text-muted">
            Page {page} of {pages}
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-2 rounded-lg bg-bg-card border border-border hover:bg-bg-card-hover disabled:opacity-40 transition"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(pages, p + 1))}
              disabled={page >= pages}
              className="p-2 rounded-lg bg-bg-card border border-border hover:bg-bg-card-hover disabled:opacity-40 transition"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
