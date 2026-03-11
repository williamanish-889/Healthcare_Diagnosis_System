import { type ReactNode } from "react";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: ReactNode;
  color: "teal" | "green" | "orange" | "red" | "purple" | "blue";
}

const colorClasses = {
  teal: "from-accent-teal/20 to-accent-teal/5 border-accent-teal/30 text-accent-teal",
  green: "from-accent-green/20 to-accent-green/5 border-accent-green/30 text-accent-green",
  orange: "from-accent-orange/20 to-accent-orange/5 border-accent-orange/30 text-accent-orange",
  red: "from-accent-red/20 to-accent-red/5 border-accent-red/30 text-accent-red",
  purple: "from-accent-purple/20 to-accent-purple/5 border-accent-purple/30 text-accent-purple",
  blue: "from-accent-blue/20 to-accent-blue/5 border-accent-blue/30 text-accent-blue",
};

const iconBg = {
  teal: "bg-accent-teal/20",
  green: "bg-accent-green/20",
  orange: "bg-accent-orange/20",
  red: "bg-accent-red/20",
  purple: "bg-accent-purple/20",
  blue: "bg-accent-blue/20",
};

export default function StatCard({ title, value, subtitle, icon, color }: StatCardProps) {
  return (
    <div
      className={`rounded-2xl border bg-gradient-to-br p-5 transition-all duration-300 hover:scale-[1.02] ${colorClasses[color]}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-text-muted">
            {title}
          </p>
          <p className="mt-2 text-3xl font-bold text-text-primary">{value}</p>
          {subtitle && (
            <p className="mt-1 text-sm text-text-secondary">{subtitle}</p>
          )}
        </div>
        <div className={`rounded-xl p-3 ${iconBg[color]}`}>{icon}</div>
      </div>
    </div>
  );
}
