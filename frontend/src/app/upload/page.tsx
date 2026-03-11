"use client";

import { useState, useRef } from "react";
import { Upload, FileSpreadsheet, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { uploadCSV } from "@/lib/api";

interface PredictionRow {
  row: number;
  patient_name?: string;
  predicted_disease?: string;
  confidence?: number;
  top_predictions?: { disease: string; confidence: number }[];
  error?: string;
}

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<PredictionRow[]>([]);
  const [totalRows, setTotalRows] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    setResults([]);
    try {
      const res = await uploadCSV(file);
      setResults(res.data.predictions);
      setTotalRows(res.data.total_rows);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Upload failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f && (f.name.endsWith(".csv") || f.name.endsWith(".xlsx") || f.name.endsWith(".xls"))) {
      setFile(f);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-text-primary">Upload EHR / CSV / Excel</h1>
        <p className="text-text-secondary mt-1">
          Upload patient data files for batch disease prediction
        </p>
      </div>

      {/* Upload Zone */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        className="rounded-2xl bg-bg-card border-2 border-dashed border-border hover:border-accent-teal/50 p-12 text-center transition-colors cursor-pointer"
        onClick={() => fileRef.current?.click()}
      >
        <input
          ref={fileRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="hidden"
        />
        <Upload className="w-12 h-12 text-text-muted mx-auto mb-4" />
        <p className="text-lg font-medium text-text-primary">
          {file ? file.name : "Drop CSV/Excel file here or click to browse"}
        </p>
        <p className="text-sm text-text-muted mt-2">
          Supports .csv, .xlsx, .xls files with patient data columns
        </p>
        {file && (
          <p className="text-sm text-accent-teal mt-2">
            {(file.size / 1024).toFixed(1)} KB ready for upload
          </p>
        )}
      </div>

      {file && (
        <button
          onClick={handleUpload}
          disabled={loading}
          className="w-full py-3.5 rounded-xl bg-gradient-to-r from-accent-teal to-accent-blue text-white font-semibold text-sm hover:opacity-90 disabled:opacity-50 transition flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Processing {file.name}...
            </>
          ) : (
            <>
              <FileSpreadsheet className="w-5 h-5" />
              Analyze File
            </>
          )}
        </button>
      )}

      {error && (
        <div className="flex items-center gap-2 text-accent-red text-sm bg-accent-red/10 rounded-xl p-4">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Results Table */}
      {results.length > 0 && (
        <div className="rounded-2xl bg-bg-card border border-border overflow-hidden">
          <div className="p-5 border-b border-border">
            <h3 className="text-lg font-semibold text-text-primary">
              Batch Prediction Results
            </h3>
            <p className="text-sm text-text-muted">
              Analyzed {totalRows} patient records
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left px-5 py-3 text-xs font-semibold text-text-muted uppercase">Row</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-text-muted uppercase">Patient</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-text-muted uppercase">Predicted Disease</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-text-muted uppercase">Confidence</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-text-muted uppercase">Status</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r) => (
                  <tr key={r.row} className="border-b border-border/50 hover:bg-bg-card-hover transition">
                    <td className="px-5 py-3 text-text-muted">#{r.row}</td>
                    <td className="px-5 py-3 text-text-primary">{r.patient_name || "—"}</td>
                    <td className="px-5 py-3 text-accent-teal font-medium">
                      {r.predicted_disease || r.error || "—"}
                    </td>
                    <td className="px-5 py-3">
                      {r.confidence !== undefined && (
                        <div className="flex items-center gap-2">
                          <div className="w-20 h-1.5 rounded-full bg-bg-primary overflow-hidden">
                            <div
                              className="h-full rounded-full bg-accent-teal"
                              style={{ width: `${r.confidence}%` }}
                            />
                          </div>
                          <span className="text-xs text-text-muted">
                            {r.confidence}%
                          </span>
                        </div>
                      )}
                    </td>
                    <td className="px-5 py-3">
                      {r.error ? (
                        <AlertCircle className="w-4 h-4 text-accent-red" />
                      ) : (
                        <CheckCircle className="w-4 h-4 text-accent-green" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Format Guide */}
      <div className="rounded-2xl bg-bg-card border border-border p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-4">
          Expected CSV/Excel Format
        </h3>
        <div className="overflow-x-auto">
          <table className="text-xs text-text-secondary">
            <thead>
              <tr className="border-b border-border">
                {["age", "gender", "symptoms", "smoking", "vs_blood_pressure_systolic", "lab_hemoglobin", "..."].map((h) => (
                  <th key={h} className="px-3 py-2 text-left text-text-muted">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr>
                {["45", "male", "fever|cough|fatigue", "true", "130", "12.5", "..."].map((v, i) => (
                  <td key={i} className="px-3 py-2">{v}</td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-xs text-text-muted mt-3">
          Symptoms should be pipe-separated (|). Vital signs prefixed with vs_, lab results with lab_.
          Download the synthetic data CSV for a complete template.
        </p>
      </div>
    </div>
  );
}
