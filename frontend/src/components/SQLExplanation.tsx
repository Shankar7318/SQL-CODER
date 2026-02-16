import { useState } from "react";
import { Lightbulb, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface SqlExplanationProps {
  sql: string;
  explanation: string | null;
  isLoading: boolean;
  onExplain: (sql: string) => void;
}

export function SqlExplanation({ sql, explanation, isLoading, onExplain }: SqlExplanationProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!sql) return null;

  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      <div className="flex items-center justify-between border-b border-border px-4 py-2">
        <div className="flex items-center gap-2">
          <Lightbulb className="h-3.5 w-3.5 text-warning" />
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            SQL Explanation
          </span>
        </div>
        <div className="flex items-center gap-2">
          {!explanation && !isLoading && (
            <button
              onClick={() => onExplain(sql)}
              className="rounded-md bg-primary/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-primary transition-colors hover:bg-primary/20"
            >
              Explain
            </button>
          )}
          {explanation && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="rounded-md p-1 text-muted-foreground hover:text-foreground"
            >
              {isExpanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
            </button>
          )}
        </div>
      </div>

      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2 p-4"
          >
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
            <span className="text-sm text-muted-foreground">Analyzing query...</span>
          </motion.div>
        )}

        {explanation && isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="p-4 text-sm leading-relaxed text-foreground whitespace-pre-wrap">
              {explanation}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
