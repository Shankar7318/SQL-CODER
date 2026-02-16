import { Clock, CheckCircle2, XCircle } from "lucide-react";
import { motion } from "framer-motion";
import type { QueryHistoryItem } from "@/hooks/useTextToSql";

interface QueryHistoryProps {
  history: QueryHistoryItem[];
  onSelect: (item: QueryHistoryItem) => void;
}

export function QueryHistory({ history, onSelect }: QueryHistoryProps) {
  if (history.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-border bg-card/50 p-6 text-center">
        <Clock className="mx-auto h-8 w-8 text-muted-foreground/50" />
        <p className="mt-2 text-sm text-muted-foreground">No queries yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {history.map((item, i) => (
        <motion.button
          key={item.id}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.05 }}
          onClick={() => onSelect(item)}
          className="w-full rounded-lg border border-border bg-card p-3 text-left transition-all hover:border-primary/30 hover:bg-muted/50"
        >
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm text-foreground line-clamp-1">
              {item.naturalQuery}
            </p>
            {item.status === "success" ? (
              <CheckCircle2 className="h-4 w-4 shrink-0 text-success" />
            ) : (
              <XCircle className="h-4 w-4 shrink-0 text-destructive" />
            )}
          </div>
          <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
            <span>{item.timestamp.toLocaleTimeString()}</span>
            {item.executionTime && (
              <span>• {item.executionTime}ms</span>
            )}
          </div>
        </motion.button>
      ))}
    </div>
  );
}
