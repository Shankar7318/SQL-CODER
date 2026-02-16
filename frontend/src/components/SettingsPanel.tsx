import { useState } from "react";
import { Settings, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import type { ApiConfig } from "@/hooks/useTextToSql";

interface SettingsPanelProps {
  config: ApiConfig;
  onChange: (config: ApiConfig) => void;
}

export function SettingsPanel({ config, onChange }: SettingsPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="rounded-md border border-border bg-card p-2 text-muted-foreground transition-colors hover:text-foreground hover:border-primary/30"
      >
        <Settings className="h-4 w-4" />
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 z-40 bg-background/60 backdrop-blur-sm"
            />
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="fixed right-0 top-0 z-50 h-full w-80 border-l border-border bg-card p-6 shadow-xl"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-sm font-semibold uppercase tracking-wider text-foreground">
                  API Settings
                </h2>
                <button
                  onClick={() => setIsOpen(false)}
                  className="rounded-md p-1 text-muted-foreground hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="mb-1.5 block text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Base URL
                  </label>
                  <input
                    type="text"
                    value={config.baseUrl}
                    onChange={(e) => onChange({ ...config, baseUrl: e.target.value })}
                    className="w-full rounded-md border border-border bg-input px-3 py-2 font-mono text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    placeholder="http://localhost:8000"
                  />
                </div>
                <div>
                  <label className="mb-1.5 block text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Endpoint
                  </label>
                  <input
                    type="text"
                    value={config.endpoint}
                    onChange={(e) => onChange({ ...config, endpoint: e.target.value })}
                    className="w-full rounded-md border border-border bg-input px-3 py-2 font-mono text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    placeholder="/api/text-to-sql"
                  />
                </div>
                <div className="rounded-md border border-border bg-muted/50 p-3">
                  <p className="text-xs text-muted-foreground font-mono">
                    Full URL: {config.baseUrl}{config.endpoint}
                  </p>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
