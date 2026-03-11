"use client";

import { useEffect, useState, useCallback } from "react";
import { Search, ChevronLeft, ChevronRight, User } from "lucide-react";
import { getPatients, type Patient } from "@/lib/api";

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [search, setSearch] = useState("");
  const [diagnosis, setDiagnosis] = useState("");
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Patient | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getPatients({ page, limit: 20, search, diagnosis });
      setPatients(res.data.patients);
      setTotal(res.data.total);
      setPages(res.data.pages);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page, search, diagnosis]);

  useEffect(() => {
    load();
  }, [load]);

  const severityColor: Record<string, string> = {
    Mild: "text-accent-green bg-accent-green/15",
    Moderate: "text-accent-orange bg-accent-orange/15",
    Severe: "text-accent-red bg-accent-red/15",
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Patient Records</h1>
          <p className="text-text-secondary mt-1">
            {total.toLocaleString()} patients in database
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            type="text"
            placeholder="Search by name or patient ID..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-bg-card border border-border text-text-primary placeholder:text-text-muted text-sm focus:outline-none focus:border-accent-teal transition"
          />
        </div>
        <input
          type="text"
          placeholder="Filter by diagnosis..."
          value={diagnosis}
          onChange={(e) => {
            setDiagnosis(e.target.value);
            setPage(1);
          }}
          className="px-4 py-2.5 rounded-xl bg-bg-card border border-border text-text-primary placeholder:text-text-muted text-sm focus:outline-none focus:border-accent-teal transition w-64"
        />
      </div>

      {/* Patient Detail Modal */}
      {selected && (
        <div
          className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"
          onClick={() => setSelected(null)}
        >
          <div
            className="bg-bg-card border border-border rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-accent-teal/20 flex items-center justify-center">
                  <User className="w-6 h-6 text-accent-teal" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-text-primary">
                    {selected.first_name} {selected.last_name}
                  </h2>
                  <p className="text-sm text-text-muted">
                    {selected.patient_id} &middot; {selected.age}y &middot; {selected.gender}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelected(null)}
                className="text-text-muted hover:text-text-primary text-2xl"
              >
                &times;
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <Info label="Country" value={`${selected.city || ""}, ${selected.state || ""}, ${selected.country}`} />
              <Info label="Blood Group" value={selected.blood_group || "N/A"} />
              <Info label="Diagnosis" value={selected.diagnosis || "Pending"} />
              <Info label="Severity" value={selected.severity || "N/A"} />
              <Info label="Smoking" value={selected.smoking ? "Yes" : "No"} />
              <Info label="Alcohol" value={selected.alcohol ? "Yes" : "No"} />
            </div>

            {selected.symptoms?.length > 0 && (
              <div className="mt-4">
                <p className="text-xs font-semibold text-text-muted uppercase mb-2">Symptoms</p>
                <div className="flex flex-wrap gap-2">
                  {selected.symptoms.map((s, i) => (
                    <span key={i} className="px-2.5 py-1 rounded-lg bg-accent-teal/10 text-accent-teal text-xs">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {selected.vital_signs && (
              <div className="mt-4">
                <p className="text-xs font-semibold text-text-muted uppercase mb-2">Vital Signs</p>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  {Object.entries(selected.vital_signs).map(([k, v]) =>
                    v ? (
                      <div key={k} className="bg-bg-primary rounded-lg p-2">
                        <span className="text-text-muted">{k.replace(/_/g, " ")}:</span>{" "}
                        <span className="text-text-primary font-medium">{String(v)}</span>
                      </div>
                    ) : null
                  )}
                </div>
              </div>
            )}

            {selected.treatment && (
              <div className="mt-4">
                <p className="text-xs font-semibold text-text-muted uppercase mb-2">Treatment</p>
                <p className="text-sm text-text-secondary">{selected.treatment}</p>
              </div>
            )}

            {selected.root_cause && (
              <div className="mt-4">
                <p className="text-xs font-semibold text-text-muted uppercase mb-2">Root Cause</p>
                <p className="text-sm text-text-secondary">{selected.root_cause}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Table */}
      <div className="rounded-2xl bg-bg-card border border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left px-5 py-4 text-xs font-semibold text-text-muted uppercase">Patient</th>
                <th className="text-left px-5 py-4 text-xs font-semibold text-text-muted uppercase">Age/Gender</th>
                <th className="text-left px-5 py-4 text-xs font-semibold text-text-muted uppercase">Country</th>
                <th className="text-left px-5 py-4 text-xs font-semibold text-text-muted uppercase">Diagnosis</th>
                <th className="text-left px-5 py-4 text-xs font-semibold text-text-muted uppercase">Severity</th>
                <th className="text-left px-5 py-4 text-xs font-semibold text-text-muted uppercase">Symptoms</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-text-muted">
                    Loading...
                  </td>
                </tr>
              ) : patients.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-text-muted">
                    No patients found. Seed the database first.
                  </td>
                </tr>
              ) : (
                patients.map((p) => (
                  <tr
                    key={p.id || p.patient_id}
                    className="border-b border-border/50 hover:bg-bg-card-hover cursor-pointer transition"
                    onClick={() => setSelected(p)}
                  >
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-accent-purple/15 flex items-center justify-center text-xs font-bold text-accent-purple">
                          {p.first_name?.[0]}
                          {p.last_name?.[0]}
                        </div>
                        <div>
                          <p className="font-medium text-text-primary">
                            {p.first_name} {p.last_name}
                          </p>
                          <p className="text-xs text-text-muted">{p.patient_id}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-text-secondary">
                      {p.age}y / {p.gender}
                    </td>
                    <td className="px-5 py-3.5 text-text-secondary">{p.country}</td>
                    <td className="px-5 py-3.5">
                      <span className="text-accent-teal font-medium">{p.diagnosis || "—"}</span>
                    </td>
                    <td className="px-5 py-3.5">
                      <span
                        className={`px-2.5 py-1 rounded-lg text-xs font-medium ${
                          severityColor[p.severity || ""] || "text-text-muted bg-bg-primary"
                        }`}
                      >
                        {p.severity || "—"}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-text-muted text-xs max-w-48 truncate">
                      {p.symptoms?.slice(0, 3).join(", ")}
                      {(p.symptoms?.length || 0) > 3 && "..."}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-5 py-4 border-t border-border">
          <p className="text-sm text-text-muted">
            Page {page} of {pages} ({total} records)
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-2 rounded-lg bg-bg-primary border border-border hover:bg-bg-card-hover disabled:opacity-40 transition"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(pages, p + 1))}
              disabled={page >= pages}
              className="p-2 rounded-lg bg-bg-primary border border-border hover:bg-bg-card-hover disabled:opacity-40 transition"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-bg-primary rounded-lg p-3">
      <p className="text-xs text-text-muted">{label}</p>
      <p className="text-text-primary font-medium mt-0.5">{value}</p>
    </div>
  );
}
