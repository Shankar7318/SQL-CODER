import { useState } from "react";
import { Database, Table, Columns, ChevronRight, ChevronDown, RefreshCw, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export interface ColumnInfo {
  name: string;
  type: string;
  nullable: boolean;
  isPrimary?: boolean;
}

export interface TableInfo {
  name: string;
  columns: ColumnInfo[];
  rowCount?: number;
}

interface SchemaViewerProps {
  tables: TableInfo[];
  isLoading: boolean;
  onRefresh: () => void;
  onTableClick?: (tableName: string) => void;
}

export function SchemaViewer({ tables, isLoading, onRefresh, onTableClick }: SchemaViewerProps) {
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set());

  const toggleTable = (name: string) => {
    setExpandedTables((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  };

  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      <div className="flex items-center justify-between border-b border-border px-4 py-2.5">
        <div className="flex items-center gap-2">
          <Database className="h-3.5 w-3.5 text-primary" />
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Schema Explorer
          </span>
        </div>
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="rounded-md p-1.5 text-muted-foreground transition-colors hover:text-foreground hover:bg-muted disabled:opacity-50"
        >
          {isLoading ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <RefreshCw className="h-3.5 w-3.5" />
          )}
        </button>
      </div>

      {tables.length === 0 ? (
        <div className="p-6 text-center">
          <Columns className="mx-auto h-8 w-8 text-muted-foreground/50" />
          <p className="mt-2 text-xs text-muted-foreground">
            {isLoading ? "Loading schema..." : "No tables found. Connect your backend to load schema."}
          </p>
        </div>
      ) : (
        <div className="max-h-[400px] overflow-y-auto">
          {tables.map((table) => (
            <div key={table.name} className="border-b border-border/50 last:border-0">
              <button
                onClick={() => toggleTable(table.name)}
                className="flex w-full items-center gap-2 px-4 py-2.5 text-left transition-colors hover:bg-muted/50"
              >
                {expandedTables.has(table.name) ? (
                  <ChevronDown className="h-3 w-3 text-muted-foreground" />
                ) : (
                  <ChevronRight className="h-3 w-3 text-muted-foreground" />
                )}
                <Table className="h-3.5 w-3.5 text-primary" />
                <span className="text-sm font-mono text-foreground">{table.name}</span>
                {table.rowCount !== undefined && (
                  <span className="ml-auto text-[10px] font-mono text-muted-foreground">
                    {table.rowCount} rows
                  </span>
                )}
              </button>

              <AnimatePresence>
                {expandedTables.has(table.name) && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="bg-muted/30 px-4 py-1">
                      {table.columns.map((col) => (
                        <div
                          key={col.name}
                          className="flex items-center gap-2 py-1.5 text-xs font-mono"
                        >
                          <span
                            className={`${col.isPrimary ? "text-warning" : "text-foreground"}`}
                          >
                            {col.isPrimary ? "🔑 " : ""}
                            {col.name}
                          </span>
                          <span className="text-accent">{col.type}</span>
                          {col.nullable && (
                            <span className="text-muted-foreground">nullable</span>
                          )}
                        </div>
                      ))}
                      {onTableClick && (
                        <button
                          onClick={() => onTableClick(table.name)}
                          className="mt-1 mb-2 text-[10px] text-primary hover:underline"
                        >
                          Query this table →
                        </button>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
