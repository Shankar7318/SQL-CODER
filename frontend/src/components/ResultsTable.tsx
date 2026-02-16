import { motion } from "framer-motion";

interface ResultsTableProps {
  results: Record<string, unknown>[] | null;
}

export function ResultsTable({ results }: ResultsTableProps) {
  if (!results || results.length === 0) return null;

  const columns = Object.keys(results[0]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-lg border border-border bg-card overflow-hidden"
    >
      <div className="flex items-center gap-2 border-b border-border px-4 py-2">
        <span className="text-xs text-muted-foreground font-mono uppercase tracking-wider">
          Results
        </span>
        <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary font-mono">
          {results.length} rows
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/50">
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-4 py-2.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground font-mono"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.map((row, i) => (
              <tr
                key={i}
                className="border-b border-border/50 transition-colors hover:bg-muted/30"
              >
                {columns.map((col) => (
                  <td key={col} className="px-4 py-2.5 font-mono text-foreground">
                    {String(row[col] ?? "NULL")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}
