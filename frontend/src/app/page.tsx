"use client";

import { useEffect, useState } from "react";
import {
  Users,
  Activity,
  ShieldCheck,
  AlertTriangle,
  Globe,
  TrendingUp,
} from "lucide-react";
import StatCard from "@/components/StatCard";
import { getStats, getHealth, type StatsData } from "@/lib/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const CHART_COLORS = [
  "#06b6d4",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#3b82f6",
  "#ec4899",
  "#14b8a6",
  "#f97316",
  "#6366f1",
];

export default function Dashboard() {
  const [stats, setStats] = useState<StatsData | null>(null);
  const [health, setHealth] = useState<{
    status: string;
    database: string;
    ml_model: string;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [statsRes, healthRes] = await Promise.all([
          getStats(),
          getHealth(),
        ]);
        setStats(statsRes.data);
        setHealth(healthRes.data);
      } catch (err) {
        console.error("Failed to load dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-accent-teal/30 border-t-accent-teal rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-text-secondary">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const topDiseases = stats?.diagnosis_distribution.slice(0, 10) || [];
  const severityData = stats?.severity_distribution || [];
  const genderData = stats?.gender_distribution || [];

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-text-primary">Dashboard</h1>
        <p className="text-text-secondary mt-1">
          Euron Healthcare Diagnosis Support System Overview
        </p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Gateway Status"
          value={health?.status === "healthy" ? "Healthy" : "Offline"}
          subtitle={health?.database === "connected" ? "DB Connected" : "DB Error"}
          icon={<ShieldCheck className="w-6 h-6" />}
          color="teal"
        />
        <StatCard
          title="Total Patients"
          value={stats?.total_patients?.toLocaleString() || "0"}
          subtitle="In database"
          icon={<Users className="w-6 h-6" />}
          color="green"
        />
        <StatCard
          title="Disease Classes"
          value={stats?.diagnosis_distribution.length || 0}
          subtitle="ML model trained"
          icon={<Activity className="w-6 h-6" />}
          color="purple"
        />
        <StatCard
          title="ML Model"
          value={health?.ml_model === "loaded" ? "Active" : "Inactive"}
          subtitle={health?.ml_model === "loaded" ? "Ready for predictions" : "Needs training"}
          icon={<TrendingUp className="w-6 h-6" />}
          color="orange"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Disease Distribution Bar Chart */}
        <div className="rounded-2xl bg-bg-card border border-border p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Disease Distribution
          </h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={topDiseases}
                layout="vertical"
                margin={{ left: 20, right: 20 }}
              >
                <XAxis type="number" stroke="#64748b" fontSize={12} />
                <YAxis
                  type="category"
                  dataKey="disease"
                  width={160}
                  stroke="#64748b"
                  fontSize={11}
                  tick={{ fill: "#94a3b8" }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1a2236",
                    border: "1px solid #1e3a5f",
                    borderRadius: "12px",
                    color: "#f1f5f9",
                  }}
                />
                <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                  {topDiseases.map((_, i) => (
                    <Cell
                      key={i}
                      fill={CHART_COLORS[i % CHART_COLORS.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity + Gender Pie Charts */}
        <div className="space-y-6">
          <div className="rounded-2xl bg-bg-card border border-border p-6">
            <h3 className="text-lg font-semibold text-text-primary mb-4">
              Severity Distribution
            </h3>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityData}
                    dataKey="count"
                    nameKey="severity"
                    cx="50%"
                    cy="50%"
                    outerRadius={70}
                    innerRadius={40}
                    paddingAngle={3}
                    label={({ severity, count }) => `${severity}: ${count}`}
                  >
                    {severityData.map((_, i) => (
                      <Cell
                        key={i}
                        fill={
                          ["#10b981", "#f59e0b", "#ef4444"][i] ||
                          CHART_COLORS[i]
                        }
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1a2236",
                      border: "1px solid #1e3a5f",
                      borderRadius: "12px",
                      color: "#f1f5f9",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rounded-2xl bg-bg-card border border-border p-6">
            <h3 className="text-lg font-semibold text-text-primary mb-4">
              Country Distribution
            </h3>
            <div className="space-y-2">
              {(stats?.country_distribution || []).slice(0, 5).map((c, i) => (
                <div key={i} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4 text-text-muted" />
                    <span className="text-sm text-text-secondary">
                      {c.country}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-32 h-2 rounded-full bg-bg-primary overflow-hidden">
                      <div
                        className="h-full rounded-full bg-accent-teal"
                        style={{
                          width: `${(c.count / (stats?.total_patients || 1)) * 100}%`,
                        }}
                      />
                    </div>
                    <span className="text-sm font-medium text-text-primary w-10 text-right">
                      {c.count}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Age Distribution */}
      <div className="rounded-2xl bg-bg-card border border-border p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-4">
          Age Group Distribution
        </h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stats?.age_distribution || []}>
              <XAxis dataKey="range" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1a2236",
                  border: "1px solid #1e3a5f",
                  borderRadius: "12px",
                  color: "#f1f5f9",
                }}
              />
              <Bar dataKey="count" fill="#06b6d4" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
