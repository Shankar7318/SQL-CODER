import { BarChart3, Clock, CheckCircle2, XCircle, Zap } from "lucide-react";
import { motion } from "framer-motion";
import type { QueryHistoryItem } from "@/hooks/useTextToSql";

interface QueryStatsProps {
  history: QueryHistoryItem[];
}

export function QueryStats({ history }: QueryStatsProps) {
  if (history.length === 0) return null;

  const totalQueries = history.length;
  const successCount = history.filter((h) => h.status === "success").length;
  const errorCount = history.filter((h) => h.status === "error").length;
  const successRate = totalQueries > 0 ? Math.round((successCount / totalQueries) * 100) : 0;

  const times = history
    .filter((h) => h.executionTime)
    .map((h) => h.executionTime!);
  const avgTime = times.length > 0 ? Math.round(times.reduce((a, b) => a + b, 0) / times.length) : 0;
  const fastestTime = times.length > 0 ? Math.min(...times) : 0;

  const stats = [
    {
      icon: BarChart3,
      label: "Total Queries",
      value: totalQueries,
      color: "text-primary",
      bg: "bg-primary/10",
    },
    {
      icon: CheckCircle2,
      label: "Success Rate",
      value: `${successRate}%`,
      color: "text-success",
      bg: "bg-success/10",
    },
    {
      icon: Clock,
      label: "Avg Time",
      value: avgTime > 0 ? `${avgTime}ms` : "—",
      color: "text-accent",
      bg: "bg-accent/10",
    },
    {
      icon: Zap,
      label: "Fastest",
      value: fastestTime > 0 ? `${fastestTime}ms` : "—",
      color: "text-warning",
      bg: "bg-warning/10",
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      className="grid grid-cols-2 gap-2 sm:grid-cols-4"
    >
      {stats.map((stat) => (
        <div
          key={stat.label}
          className="rounded-lg border border-border bg-card p-3 text-center"
        >
          <div className={`mx-auto mb-1.5 flex h-7 w-7 items-center justify-center rounded-md ${stat.bg}`}>
            <stat.icon className={`h-3.5 w-3.5 ${stat.color}`} />
          </div>
          <p className="text-lg font-bold font-mono text-foreground">{stat.value}</p>
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground">
            {stat.label}
          </p>
        </div>
      ))}
    </motion.div>
  );
}
