import { Copy, Check } from "lucide-react";
import { useState, type JSX } from "react";
import { motion } from "framer-motion";

interface SqlOutputProps {
  sql: string;
  error?: string | null;
  isLoading: boolean;
}

const SQL_KEYWORDS = [
  "SELECT", "FROM", "WHERE", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER",
  "ON", "AND", "OR", "NOT", "IN", "EXISTS", "BETWEEN", "LIKE", "IS",
  "NULL", "ORDER", "BY", "GROUP", "HAVING", "LIMIT", "OFFSET", "AS",
  "INSERT", "INTO", "VALUES", "UPDATE", "SET", "DELETE", "CREATE",
  "TABLE", "ALTER", "DROP", "INDEX", "VIEW", "DISTINCT", "COUNT",
  "SUM", "AVG", "MIN", "MAX", "CASE", "WHEN", "THEN", "ELSE", "END",
  "UNION", "ALL", "ASC", "DESC", "WITH", "RECURSIVE", "CROSS", "FULL",
  "NATURAL", "USING", "EXCEPT", "INTERSECT", "TOP", "FETCH", "NEXT",
  "ROWS", "ONLY", "OVER", "PARTITION", "ROW_NUMBER", "RANK", "DENSE_RANK",
];

function highlightSql(sql: string): JSX.Element[] {
  const tokens = sql.split(/(\s+|,|\(|\)|;|'[^']*'|\b\d+\b)/g);
  return tokens.map((token, i) => {
    const upper = token.toUpperCase();
    if (SQL_KEYWORDS.includes(upper)) {
      return <span key={i} className="text-sql-keyword font-semibold">{token}</span>;
    }
    if (/^'.*'$/.test(token)) {
      return <span key={i} className="text-sql-string">{token}</span>;
    }
    if (/^\d+$/.test(token)) {
      return <span key={i} className="text-sql-number">{token}</span>;
    }
    return <span key={i}>{token}</span>;
  });
}

export function SqlOutput({ sql, error, isLoading }: SqlOutputProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (isLoading) {
    return (
      <div className="rounded-lg border border-border bg-card p-6">
        <div className="flex items-center gap-3">
          <div className="h-2 w-2 rounded-full bg-primary animate-pulse-glow" />
          <span className="text-sm text-muted-foreground font-mono">
            Generating SQL...
          </span>
        </div>
        <div className="mt-4 space-y-2">
          <div className="h-4 w-3/4 rounded bg-muted animate-pulse" />
          <div className="h-4 w-1/2 rounded bg-muted animate-pulse" />
          <div className="h-4 w-2/3 rounded bg-muted animate-pulse" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="rounded-lg border border-destructive/50 bg-destructive/10 p-4"
      >
        <p className="text-sm text-destructive font-mono">{error}</p>
      </motion.div>
    );
  }

  if (!sql) {
    return (
      <div className="rounded-lg border border-dashed border-border bg-card/50 p-8 text-center">
        <p className="text-sm text-muted-foreground">
          Generated SQL will appear here
        </p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-lg border border-border bg-card overflow-hidden"
    >
      <div className="flex items-center justify-between border-b border-border px-4 py-2">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-success" />
          <span className="text-xs text-muted-foreground font-mono uppercase tracking-wider">
            SQL Output
          </span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-muted-foreground transition-colors hover:text-foreground hover:bg-muted"
        >
          {copied ? <Check className="h-3.5 w-3.5 text-success" /> : <Copy className="h-3.5 w-3.5" />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre className="p-4 font-mono text-sm leading-relaxed overflow-x-auto">
        <code>{highlightSql(sql)}</code>
      </pre>
    </motion.div>
  );
}
