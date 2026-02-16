import { useState } from "react";
import { Send, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

interface QueryInputProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

const EXAMPLE_QUERIES = [
  "Show all customers who made purchases last month",
  "Find the top 5 products by revenue",
  "List employees with salary above average",
  "Count orders grouped by status",
];

export function QueryInput({ onSubmit, isLoading }: QueryInputProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query.trim());
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-3"
    >
      <form onSubmit={handleSubmit} className="relative">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe your query in plain English..."
          rows={3}
          className="w-full rounded-lg border border-border bg-card p-4 pr-14 font-sans text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary resize-none transition-all"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />
        <button
          type="submit"
          disabled={!query.trim() || isLoading}
          className="absolute bottom-3 right-3 rounded-md bg-primary p-2 text-primary-foreground transition-all hover:opacity-90 disabled:opacity-30 disabled:cursor-not-allowed glow-primary"
        >
          {isLoading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Send className="h-5 w-5" />
          )}
        </button>
      </form>

      <div className="flex flex-wrap gap-2">
        {EXAMPLE_QUERIES.map((example) => (
          <button
            key={example}
            onClick={() => setQuery(example)}
            className="rounded-md border border-border bg-secondary px-3 py-1.5 text-xs text-secondary-foreground transition-colors hover:bg-muted hover:border-primary/30"
          >
            {example}
          </button>
        ))}
      </div>
    </motion.div>
  );
}
