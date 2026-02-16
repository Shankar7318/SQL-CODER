import { Download, FileJson, FileSpreadsheet } from "lucide-react";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface ExportButtonProps {
  results: Record<string, unknown>[] | null;
  sql: string;
}

export function ExportButton({ results, sql }: ExportButtonProps) {
  const [showMenu, setShowMenu] = useState(false);

  if (!results && !sql) return null;

  const exportCSV = () => {
    if (!results || results.length === 0) return;
    const cols = Object.keys(results[0]);
    const header = cols.join(",");
    const rows = results.map((r) =>
      cols.map((c) => `"${String(r[c] ?? "")}"`).join(",")
    );
    const csv = [header, ...rows].join("\n");
    downloadFile(csv, "query-results.csv", "text/csv");
    setShowMenu(false);
  };

  const exportJSON = () => {
    if (!results || results.length === 0) return;
    const json = JSON.stringify(results, null, 2);
    downloadFile(json, "query-results.json", "application/json");
    setShowMenu(false);
  };

  const exportSQL = () => {
    if (!sql) return;
    downloadFile(sql, "query.sql", "text/plain");
    setShowMenu(false);
  };

  const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowMenu(!showMenu)}
        className="flex items-center gap-1.5 rounded-md border border-border bg-card px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground hover:border-primary/30"
      >
        <Download className="h-3.5 w-3.5" />
        Export
      </button>

      <AnimatePresence>
        {showMenu && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setShowMenu(false)} />
            <motion.div
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              className="absolute right-0 top-full z-50 mt-1 w-44 rounded-lg border border-border bg-card p-1 shadow-xl"
            >
              {results && results.length > 0 && (
                <>
                  <button
                    onClick={exportCSV}
                    className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-xs text-foreground transition-colors hover:bg-muted"
                  >
                    <FileSpreadsheet className="h-3.5 w-3.5 text-success" />
                    Export as CSV
                  </button>
                  <button
                    onClick={exportJSON}
                    className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-xs text-foreground transition-colors hover:bg-muted"
                  >
                    <FileJson className="h-3.5 w-3.5 text-warning" />
                    Export as JSON
                  </button>
                </>
              )}
              {sql && (
                <button
                  onClick={exportSQL}
                  className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-xs text-foreground transition-colors hover:bg-muted"
                >
                  <Download className="h-3.5 w-3.5 text-accent" />
                  Export SQL
                </button>
              )}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
