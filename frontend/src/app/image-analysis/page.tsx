"use client";

import { useState, useRef } from "react";
import {
  ScanLine,
  Upload,
  Loader2,
  AlertCircle,
  Brain,
  Eye,
} from "lucide-react";
import { analyzeImage } from "@/lib/api";

interface AnalysisResult {
  image_type: string;
  findings: string;
  confidence: number;
  abnormalities_detected: string[];
  recommendation: string;
}

export default function ImageAnalysisPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [imageType, setImageType] = useState("xray");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (f: File | null) => {
    setFile(f);
    setResult(null);
    setError("");
    if (f) {
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result as string);
      reader.readAsDataURL(f);
    } else {
      setPreview("");
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await analyzeImage(file, imageType);
      setResult(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Analysis failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-text-primary">
          Medical Image Analysis
        </h1>
        <p className="text-text-secondary mt-1">
          Upload X-ray, MRI, or CT scans for AI-powered analysis
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Panel */}
        <div className="space-y-6">
          <div className="rounded-2xl bg-bg-card border border-border p-6">
            <h3 className="text-base font-semibold text-text-primary mb-4">
              Image Type
            </h3>
            <div className="flex gap-3">
              {[
                { value: "xray", label: "X-Ray" },
                { value: "mri", label: "MRI" },
                { value: "ct", label: "CT Scan" },
                { value: "other", label: "Other" },
              ].map((t) => (
                <button
                  key={t.value}
                  onClick={() => setImageType(t.value)}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition ${
                    imageType === t.value
                      ? "bg-accent-teal/20 text-accent-teal border border-accent-teal/40"
                      : "bg-bg-primary text-text-secondary border border-border hover:bg-bg-card-hover"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              handleFileChange(e.dataTransfer.files[0]);
            }}
            className="rounded-2xl bg-bg-card border-2 border-dashed border-border hover:border-accent-teal/50 p-8 text-center transition-colors cursor-pointer"
            onClick={() => fileRef.current?.click()}
          >
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
              className="hidden"
            />
            {preview ? (
              <img
                src={preview}
                alt="Medical scan preview"
                className="max-h-64 mx-auto rounded-xl object-contain"
              />
            ) : (
              <>
                <ScanLine className="w-12 h-12 text-text-muted mx-auto mb-4" />
                <p className="text-lg font-medium text-text-primary">
                  Drop medical image here
                </p>
                <p className="text-sm text-text-muted mt-2">
                  JPEG, PNG, DICOM &middot; Max 20MB
                </p>
              </>
            )}
          </div>

          {file && (
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-accent-purple to-accent-blue text-white font-semibold text-sm hover:opacity-90 disabled:opacity-50 transition flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing scan...
                </>
              ) : (
                <>
                  <Eye className="w-5 h-5" />
                  Analyze Image
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
        </div>

        {/* Results Panel */}
        <div className="space-y-4">
          {result ? (
            <>
              <div className="rounded-2xl bg-bg-card border border-accent-teal/30 p-6">
                <div className="flex items-center gap-2 mb-3">
                  <Brain className="w-5 h-5 text-accent-teal" />
                  <h3 className="font-semibold text-text-primary">
                    Analysis Results
                  </h3>
                </div>
                <div className="flex items-center gap-3 mb-4">
                  <span className="px-3 py-1 rounded-lg bg-accent-purple/15 text-accent-purple text-xs font-medium uppercase">
                    {result.image_type}
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 rounded-full bg-bg-primary overflow-hidden">
                      <div
                        className="h-full rounded-full bg-accent-teal"
                        style={{ width: `${result.confidence}%` }}
                      />
                    </div>
                    <span className="text-sm font-bold text-accent-teal">
                      {result.confidence}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="rounded-2xl bg-bg-card border border-border p-6">
                <h3 className="font-semibold text-text-primary mb-3">
                  Findings
                </h3>
                <p className="text-sm text-text-secondary leading-relaxed">
                  {result.findings}
                </p>
              </div>

              {result.abnormalities_detected.length > 0 && (
                <div className="rounded-2xl bg-bg-card border border-accent-orange/30 p-6">
                  <h3 className="font-semibold text-text-primary mb-3">
                    Abnormalities Detected
                  </h3>
                  <ul className="space-y-2">
                    {result.abnormalities_detected.map((a, i) => (
                      <li
                        key={i}
                        className="flex items-center gap-2 text-sm text-text-secondary"
                      >
                        <AlertCircle className="w-4 h-4 text-accent-orange flex-shrink-0" />
                        {a}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="rounded-2xl bg-bg-card border border-accent-green/30 p-6">
                <h3 className="font-semibold text-text-primary mb-3">
                  Recommendation
                </h3>
                <p className="text-sm text-text-secondary leading-relaxed">
                  {result.recommendation}
                </p>
              </div>
            </>
          ) : (
            <div className="rounded-2xl bg-bg-card border border-border p-12 text-center">
              <ScanLine className="w-16 h-16 text-text-muted mx-auto mb-4" />
              <p className="text-text-secondary text-lg">
                Upload a medical image to start analysis
              </p>
              <p className="text-text-muted text-sm mt-2">
                Powered by GPT-4o Vision & Hugging Face models
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
