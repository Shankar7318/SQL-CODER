import { useState } from "react";
import { Bookmark, BookmarkPlus, Trash2, Play } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export interface SavedQuery {
  id: string;
  name: string;
  naturalQuery: string;
  sqlQuery: string;
  savedAt: Date;
}

interface SavedQueriesProps {
  savedQueries: SavedQuery[];
  onSave: (name: string, naturalQuery: string, sqlQuery: string) => void;
  onDelete: (id: string) => void;
  onRun: (query: SavedQuery) => void;
  currentNaturalQuery?: string;
  currentSql?: string;
}

export function SavedQueries({
  savedQueries,
  onSave,
  onDelete,
  onRun,
  currentNaturalQuery,
  currentSql,
}: SavedQueriesProps) {
  const [isAdding, setIsAdding] = useState(false);
  const [newName, setNewName] = useState("");

  const handleSave = () => {
    if (newName.trim() && currentNaturalQuery && currentSql) {
      onSave(newName.trim(), currentNaturalQuery, currentSql);
      setNewName("");
      setIsAdding(false);
    }
  };

  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      <div className="flex items-center justify-between border-b border-border px-4 py-2.5">
        <div className="flex items-center gap-2">
          <Bookmark className="h-3.5 w-3.5 text-accent" />
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Saved Queries
          </span>
        </div>
        {currentSql && (
          <button
            onClick={() => setIsAdding(true)}
            className="rounded-md p-1.5 text-muted-foreground transition-colors hover:text-foreground hover:bg-muted"
          >
            <BookmarkPlus className="h-3.5 w-3.5" />
          </button>
        )}
      </div>

      <AnimatePresence>
        {isAdding && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden border-b border-border"
          >
            <div className="p-3 space-y-2">
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Query name..."
                className="w-full rounded-md border border-border bg-input px-3 py-1.5 text-xs font-mono text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                onKeyDown={(e) => e.key === "Enter" && handleSave()}
                autoFocus
              />
              <div className="flex gap-2">
                <button
                  onClick={handleSave}
                  disabled={!newName.trim()}
                  className="rounded-md bg-primary px-3 py-1 text-[10px] font-semibold uppercase text-primary-foreground disabled:opacity-50"
                >
                  Save
                </button>
                <button
                  onClick={() => setIsAdding(false)}
                  className="rounded-md px-3 py-1 text-[10px] uppercase text-muted-foreground hover:text-foreground"
                >
                  Cancel
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {savedQueries.length === 0 ? (
        <div className="p-6 text-center">
          <Bookmark className="mx-auto h-8 w-8 text-muted-foreground/50" />
          <p className="mt-2 text-xs text-muted-foreground">No saved queries yet</p>
        </div>
      ) : (
        <div className="max-h-[300px] overflow-y-auto">
          {savedQueries.map((q) => (
            <div
              key={q.id}
              className="flex items-center justify-between border-b border-border/50 px-4 py-2.5 last:border-0 hover:bg-muted/30 transition-colors"
            >
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-foreground truncate">{q.name}</p>
                <p className="text-[10px] text-muted-foreground font-mono truncate">
                  {q.naturalQuery}
                </p>
              </div>
              <div className="flex items-center gap-1 ml-2">
                <button
                  onClick={() => onRun(q)}
                  className="rounded-md p-1.5 text-primary transition-colors hover:bg-primary/10"
                >
                  <Play className="h-3 w-3" />
                </button>
                <button
                  onClick={() => onDelete(q.id)}
                  className="rounded-md p-1.5 text-muted-foreground transition-colors hover:text-destructive hover:bg-destructive/10"
                >
                  <Trash2 className="h-3 w-3" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
