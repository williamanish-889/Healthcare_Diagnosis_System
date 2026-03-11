"use client";

import { useState, useEffect } from "react";
import {
  Stethoscope,
  Brain,
  AlertCircle,
  CheckCircle,
  ChevronDown,
  Loader2,
} from "lucide-react";
import {
  predictDiagnosis,
  getSymptoms,
  type DiagnosisRequest,
  type DiagnosisResponse,
} from "@/lib/api";

export default function DiagnosisPage() {
  const [availableSymptoms, setAvailableSymptoms] = useState<string[]>([]);
  const [form, setForm] = useState<DiagnosisRequest>({
    age: 30,
    gender: "male",
    symptoms: [],
    symptom_duration_days: 7,
    smoking: false,
    alcohol: false,
    existing_conditions: [],
    family_history: [],
    vital_signs: {},
    lab_results: {},
  });
  const [result, setResult] = useState<DiagnosisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [symptomSearch, setSymptomSearch] = useState("");
  const [showSymptoms, setShowSymptoms] = useState(false);
  const [showVitals, setShowVitals] = useState(false);
  const [showLabs, setShowLabs] = useState(false);

  useEffect(() => {
    getSymptoms()
      .then((res) => setAvailableSymptoms(res.data.symptoms))
      .catch(console.error);
  }, []);

  const filteredSymptoms = availableSymptoms.filter(
    (s) =>
      s.toLowerCase().includes(symptomSearch.toLowerCase()) &&
      !form.symptoms.includes(s)
  );

  const handleSubmit = async () => {
    if (form.symptoms.length === 0) {
      setError("Please select at least one symptom");
      return;
    }
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const res = await predictDiagnosis(form);
      setResult(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Prediction failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const toggleSymptom = (s: string) => {
    setForm((prev) => ({
      ...prev,
      symptoms: prev.symptoms.includes(s)
        ? prev.symptoms.filter((x) => x !== s)
        : [...prev.symptoms, s],
    }));
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-text-primary">AI Diagnosis</h1>
        <p className="text-text-secondary mt-1">
          Enter patient information for ML-powered disease prediction
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Input Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Demographics */}
          <Section title="Patient Demographics">
            <div className="grid grid-cols-3 gap-4">
              <Field label="Age">
                <input
                  type="number"
                  value={form.age}
                  onChange={(e) =>
                    setForm({ ...form, age: parseInt(e.target.value) || 0 })
                  }
                  className="input-field"
                />
              </Field>
              <Field label="Gender">
                <select
                  value={form.gender}
                  onChange={(e) => setForm({ ...form, gender: e.target.value })}
                  className="input-field"
                >
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </Field>
              <Field label="Symptom Duration (days)">
                <input
                  type="number"
                  value={form.symptom_duration_days || ""}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      symptom_duration_days: parseInt(e.target.value) || 0,
                    })
                  }
                  className="input-field"
                />
              </Field>
            </div>
            <div className="flex gap-6 mt-4">
              <label className="flex items-center gap-2 text-sm text-text-secondary cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.smoking}
                  onChange={(e) =>
                    setForm({ ...form, smoking: e.target.checked })
                  }
                  className="w-4 h-4 rounded bg-bg-primary border-border accent-accent-teal"
                />
                Smoking
              </label>
              <label className="flex items-center gap-2 text-sm text-text-secondary cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.alcohol}
                  onChange={(e) =>
                    setForm({ ...form, alcohol: e.target.checked })
                  }
                  className="w-4 h-4 rounded bg-bg-primary border-border accent-accent-teal"
                />
                Alcohol
              </label>
            </div>
          </Section>

          {/* Symptoms */}
          <Section title="Symptoms">
            <div className="relative">
              <input
                type="text"
                placeholder="Search symptoms..."
                value={symptomSearch}
                onChange={(e) => setSymptomSearch(e.target.value)}
                onFocus={() => setShowSymptoms(true)}
                className="input-field w-full"
              />
              {showSymptoms && filteredSymptoms.length > 0 && (
                <div className="absolute z-10 top-full mt-1 w-full max-h-48 overflow-y-auto rounded-xl bg-bg-secondary border border-border shadow-xl">
                  {filteredSymptoms.slice(0, 20).map((s) => (
                    <button
                      key={s}
                      onClick={() => {
                        toggleSymptom(s);
                        setSymptomSearch("");
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-text-secondary hover:bg-bg-card-hover hover:text-text-primary transition"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {form.symptoms.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {form.symptoms.map((s) => (
                  <span
                    key={s}
                    className="px-3 py-1.5 rounded-lg bg-accent-teal/15 text-accent-teal text-xs font-medium flex items-center gap-1.5"
                  >
                    {s}
                    <button
                      onClick={() => toggleSymptom(s)}
                      className="hover:text-white ml-1"
                    >
                      &times;
                    </button>
                  </span>
                ))}
              </div>
            )}
            {showSymptoms && (
              <button
                onClick={() => setShowSymptoms(false)}
                className="text-xs text-text-muted mt-2 hover:text-text-secondary"
              >
                Close dropdown
              </button>
            )}
          </Section>

          {/* Vital Signs (Collapsible) */}
          <div className="rounded-2xl bg-bg-card border border-border overflow-hidden">
            <button
              onClick={() => setShowVitals(!showVitals)}
              className="w-full flex items-center justify-between p-5 hover:bg-bg-card-hover transition"
            >
              <h3 className="text-base font-semibold text-text-primary">
                Vital Signs (Optional)
              </h3>
              <ChevronDown
                className={`w-5 h-5 text-text-muted transition-transform ${
                  showVitals ? "rotate-180" : ""
                }`}
              />
            </button>
            {showVitals && (
              <div className="px-5 pb-5 grid grid-cols-3 gap-4">
                {[
                  ["blood_pressure_systolic", "BP Systolic (mmHg)"],
                  ["blood_pressure_diastolic", "BP Diastolic (mmHg)"],
                  ["heart_rate", "Heart Rate (bpm)"],
                  ["temperature", "Temperature (°F)"],
                  ["respiratory_rate", "Resp. Rate (/min)"],
                  ["oxygen_saturation", "SpO2 (%)"],
                ].map(([key, label]) => (
                  <Field key={key} label={label}>
                    <input
                      type="number"
                      step="0.1"
                      value={
                        (
                          form.vital_signs as Record<string, number | undefined>
                        )?.[key] ?? ""
                      }
                      onChange={(e) =>
                        setForm({
                          ...form,
                          vital_signs: {
                            ...form.vital_signs,
                            [key]: parseFloat(e.target.value) || undefined,
                          },
                        })
                      }
                      className="input-field"
                    />
                  </Field>
                ))}
              </div>
            )}
          </div>

          {/* Lab Results (Collapsible) */}
          <div className="rounded-2xl bg-bg-card border border-border overflow-hidden">
            <button
              onClick={() => setShowLabs(!showLabs)}
              className="w-full flex items-center justify-between p-5 hover:bg-bg-card-hover transition"
            >
              <h3 className="text-base font-semibold text-text-primary">
                Lab Results (Optional)
              </h3>
              <ChevronDown
                className={`w-5 h-5 text-text-muted transition-transform ${
                  showLabs ? "rotate-180" : ""
                }`}
              />
            </button>
            {showLabs && (
              <div className="px-5 pb-5 grid grid-cols-3 gap-4">
                {[
                  ["hemoglobin", "Hemoglobin (g/dL)"],
                  ["wbc_count", "WBC Count"],
                  ["platelet_count", "Platelet Count"],
                  ["blood_sugar_fasting", "Fasting Sugar (mg/dL)"],
                  ["blood_sugar_pp", "PP Sugar (mg/dL)"],
                  ["hba1c", "HbA1c (%)"],
                  ["cholesterol_total", "Total Cholesterol"],
                  ["cholesterol_ldl", "LDL"],
                  ["cholesterol_hdl", "HDL"],
                  ["creatinine", "Creatinine"],
                  ["sgot", "SGOT"],
                  ["sgpt", "SGPT"],
                  ["tsh", "TSH (mIU/L)"],
                  ["vitamin_d", "Vitamin D (ng/mL)"],
                  ["vitamin_b12", "Vitamin B12"],
                ].map(([key, label]) => (
                  <Field key={key} label={label}>
                    <input
                      type="number"
                      step="0.01"
                      value={
                        (
                          form.lab_results as Record<string, number | undefined>
                        )?.[key] ?? ""
                      }
                      onChange={(e) =>
                        setForm({
                          ...form,
                          lab_results: {
                            ...form.lab_results,
                            [key]: parseFloat(e.target.value) || undefined,
                          },
                        })
                      }
                      className="input-field"
                    />
                  </Field>
                ))}
              </div>
            )}
          </div>

          {error && (
            <div className="flex items-center gap-2 text-accent-red text-sm">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-accent-teal to-accent-blue text-white font-semibold text-sm hover:opacity-90 disabled:opacity-50 transition flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Brain className="w-5 h-5" />
                Run AI Diagnosis
              </>
            )}
          </button>
        </div>

        {/* Results Panel */}
        <div className="space-y-4">
          {result ? (
            <>
              {/* Primary Prediction */}
              <div className="rounded-2xl bg-bg-card border border-accent-teal/30 p-6 animate-pulse-glow">
                <div className="flex items-center gap-2 mb-3">
                  <Stethoscope className="w-5 h-5 text-accent-teal" />
                  <h3 className="font-semibold text-text-primary">
                    Primary Diagnosis
                  </h3>
                </div>
                <p className="text-2xl font-bold text-accent-teal">
                  {result.predicted_disease}
                </p>
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 h-2 rounded-full bg-bg-primary overflow-hidden">
                    <div
                      className="h-full rounded-full bg-accent-teal transition-all duration-1000"
                      style={{ width: `${result.confidence}%` }}
                    />
                  </div>
                  <span className="text-sm font-bold text-accent-teal">
                    {result.confidence}%
                  </span>
                </div>
              </div>

              {/* Top Predictions */}
              <div className="rounded-2xl bg-bg-card border border-border p-6">
                <h3 className="font-semibold text-text-primary mb-3">
                  Differential Diagnoses
                </h3>
                <div className="space-y-2">
                  {result.top_predictions.map((p, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between py-2"
                    >
                      <span className="text-sm text-text-secondary">
                        {i + 1}. {p.disease}
                      </span>
                      <span className="text-xs font-medium text-text-muted">
                        {p.confidence}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* AI Suggestion */}
              {result.ai_suggestion && (
                <div className="rounded-2xl bg-bg-card border border-accent-purple/30 p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <Brain className="w-5 h-5 text-accent-purple" />
                    <h3 className="font-semibold text-text-primary">
                      AI Clinical Assessment
                    </h3>
                  </div>
                  <p className="text-sm text-text-secondary leading-relaxed">
                    {result.ai_suggestion}
                  </p>
                </div>
              )}

              {/* Root Cause */}
              {result.root_cause && (
                <div className="rounded-2xl bg-bg-card border border-accent-orange/30 p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertCircle className="w-5 h-5 text-accent-orange" />
                    <h3 className="font-semibold text-text-primary">
                      Root Cause
                    </h3>
                  </div>
                  <p className="text-sm text-text-secondary leading-relaxed">
                    {result.root_cause}
                  </p>
                </div>
              )}

              {/* Recommended Tests */}
              {result.recommended_tests.length > 0 && (
                <div className="rounded-2xl bg-bg-card border border-border p-6">
                  <h3 className="font-semibold text-text-primary mb-3">
                    Recommended Tests
                  </h3>
                  <ul className="space-y-1.5">
                    {result.recommended_tests.map((t, i) => (
                      <li
                        key={i}
                        className="flex items-center gap-2 text-sm text-text-secondary"
                      >
                        <CheckCircle className="w-3.5 h-3.5 text-accent-green flex-shrink-0" />
                        {t}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Treatment */}
              {result.recommended_treatments.length > 0 && (
                <div className="rounded-2xl bg-bg-card border border-accent-green/30 p-6">
                  <h3 className="font-semibold text-text-primary mb-3">
                    Treatment Plan
                  </h3>
                  {result.recommended_treatments.map((t, i) => (
                    <p
                      key={i}
                      className="text-sm text-text-secondary leading-relaxed"
                    >
                      {t}
                    </p>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="rounded-2xl bg-bg-card border border-border p-8 text-center">
              <Stethoscope className="w-12 h-12 text-text-muted mx-auto mb-3" />
              <p className="text-text-secondary">
                Enter patient data and run diagnosis to see results
              </p>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        :global(.input-field) {
          width: 100%;
          padding: 0.625rem 0.875rem;
          border-radius: 0.75rem;
          background-color: var(--color-bg-primary);
          border: 1px solid var(--color-border);
          color: var(--color-text-primary);
          font-size: 0.875rem;
          outline: none;
          transition: border-color 0.2s;
        }
        :global(.input-field:focus) {
          border-color: var(--color-accent-teal);
        }
        :global(.input-field::placeholder) {
          color: var(--color-text-muted);
        }
      `}</style>
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl bg-bg-card border border-border p-5">
      <h3 className="text-base font-semibold text-text-primary mb-4">
        {title}
      </h3>
      {children}
    </div>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-text-muted mb-1.5">
        {label}
      </label>
      {children}
    </div>
  );
}
