import { useState } from "react";
import { createPortal } from "react-dom";
import { Database, Loader2, CheckCircle2, XCircle, Eye, EyeOff, Link, FormInput } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export interface DbConfig {
  host: string;
  port: string;
  database: string;
  username: string;
  password: string;
  db_type: string;
}

interface DatabaseConnectionProps {
  apiBaseUrl: string;
  onConnected?: (config: DbConfig) => void;
}

const DB_TYPES = [
  { value: "postgresql", label: "PostgreSQL" },
  { value: "mysql", label: "MySQL" },
  { value: "sqlite", label: "SQLite" },
  { value: "mssql", label: "SQL Server" },
];

const DEFAULT_PORTS: Record<string, string> = {
  postgresql: "5432",
  mysql: "3306",
  sqlite: "",
  mssql: "1433",
};

export function DatabaseConnection({ apiBaseUrl, onConnected }: DatabaseConnectionProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<"idle" | "success" | "error">("idle");
  const [statusMessage, setStatusMessage] = useState("");
  const [inputMode, setInputMode] = useState<"form" | "uri">("form");
  const [connectionString, setConnectionString] = useState("");

  const [config, setConfig] = useState<DbConfig>({
    host: "localhost",
    port: "5432",
    database: "",
    username: "",
    password: "",
    db_type: "postgresql",
  });

  const parseConnectionString = (uri: string) => {
    try {
      // Formats: postgresql://user:pass@host:port/dbname, mysql://user:pass@host:port/dbname
      const match = uri.match(/^(\w+):\/\/(?:([^:@]+)(?::([^@]*))?@)?([^:\/]+)(?::(\d+))?\/(.+?)(?:\?.*)?$/);
      if (match) {
        const [, scheme, user, pass, host, port, db] = match;
        const dbType = scheme === "postgres" ? "postgresql" : scheme;
        setConfig({
          db_type: dbType,
          username: user || "",
          password: pass || "",
          host: host || "localhost",
          port: port || DEFAULT_PORTS[dbType] || "",
          database: db || "",
        });
      }
    } catch {}
  };

  const handleDbTypeChange = (type: string) => {
    setConfig((prev) => ({
      ...prev,
      db_type: type,
      port: DEFAULT_PORTS[type] || prev.port,
    }));
  };

  const updateField = (field: keyof DbConfig, value: string) => {
    setConfig((prev) => ({ ...prev, [field]: value }));
  };

  const handleConnect = async () => {
    setIsConnecting(true);
    setConnectionStatus("idle");
    setStatusMessage("");

    try {
      const payload = inputMode === "uri"
        ? { connection_string: connectionString }
        : config;
      const response = await fetch(`${apiBaseUrl}/api/connect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || errData.message || `Connection failed (${response.status})`);
      }

      const data = await response.json();
      setConnectionStatus("success");
      setStatusMessage(data.message || "Connected successfully!");
      onConnected?.(config);
    } catch (err) {
      setConnectionStatus("error");
      setStatusMessage(err instanceof Error ? err.message : "Connection failed");
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      await fetch(`${apiBaseUrl}/api/disconnect`, { method: "POST" });
    } catch {}
    setConnectionStatus("idle");
    setStatusMessage("");
  };

  const isSqlite = config.db_type === "sqlite";

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className={`relative rounded-md border p-2 transition-colors ${
          connectionStatus === "success"
            ? "border-primary/50 bg-primary/10 text-primary"
            : "border-border bg-card text-muted-foreground hover:text-foreground hover:border-primary/30"
        }`}
      >
        <Database className="h-4 w-4" />
        {connectionStatus === "success" && (
          <span className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-primary" />
        )}
      </button>

      {createPortal(
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
              className="fixed right-0 top-0 z-50 h-full w-96 overflow-y-auto border-l border-border bg-card p-6 shadow-xl"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-sm font-semibold uppercase tracking-wider text-foreground">
                  Database Connection
                </h2>
                <button
                  onClick={() => setIsOpen(false)}
                  className="rounded-md p-1 text-muted-foreground hover:text-foreground"
                >
                  <XCircle className="h-4 w-4" />
                </button>
              </div>

              <div className="space-y-4">
                {/* Mode Toggle */}
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => setInputMode("form")}
                    className={`flex items-center justify-center gap-1.5 rounded-md border px-3 py-2 text-xs font-medium transition-colors ${
                      inputMode === "form"
                        ? "border-primary bg-primary/10 text-primary"
                        : "border-border bg-muted/50 text-muted-foreground hover:text-foreground hover:border-primary/30"
                    }`}
                  >
                    <FormInput className="h-3.5 w-3.5" />
                    Form
                  </button>
                  <button
                    onClick={() => setInputMode("uri")}
                    className={`flex items-center justify-center gap-1.5 rounded-md border px-3 py-2 text-xs font-medium transition-colors ${
                      inputMode === "uri"
                        ? "border-primary bg-primary/10 text-primary"
                        : "border-border bg-muted/50 text-muted-foreground hover:text-foreground hover:border-primary/30"
                    }`}
                  >
                    <Link className="h-3.5 w-3.5" />
                    Connection URI
                  </button>
                </div>

                {inputMode === "uri" ? (
                  <div className="space-y-3">
                    <div>
                      <label className="mb-1.5 block text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Connection String
                      </label>
                      <textarea
                        value={connectionString}
                        onChange={(e) => {
                          setConnectionString(e.target.value);
                          parseConnectionString(e.target.value);
                        }}
                        className="w-full rounded-md border border-border bg-input px-3 py-2 font-mono text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 min-h-[80px] resize-none"
                        placeholder="postgresql://user:password@host:5432/dbname"
                      />
                    </div>
                    <div className="rounded-md border border-border bg-muted/30 p-3 space-y-1">
                      <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider mb-1.5">Parsed Values</p>
                      <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-[11px] font-mono">
                        <span className="text-muted-foreground">Type:</span>
                        <span className="text-foreground">{config.db_type || "—"}</span>
                        <span className="text-muted-foreground">Host:</span>
                        <span className="text-foreground">{config.host || "—"}</span>
                        <span className="text-muted-foreground">Port:</span>
                        <span className="text-foreground">{config.port || "—"}</span>
                        <span className="text-muted-foreground">Database:</span>
                        <span className="text-foreground">{config.database || "—"}</span>
                        <span className="text-muted-foreground">User:</span>
                        <span className="text-foreground">{config.username || "—"}</span>
                      </div>
                    </div>
                  </div>
                ) : (
                <>
                {/* DB Type */}
                <div>
                  <label className="mb-1.5 block text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Database Type
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {DB_TYPES.map((db) => (
                      <button
                        key={db.value}
                        onClick={() => handleDbTypeChange(db.value)}
                        className={`rounded-md border px-3 py-2 text-xs font-medium transition-colors ${
                          config.db_type === db.value
                            ? "border-primary bg-primary/10 text-primary"
                            : "border-border bg-muted/50 text-muted-foreground hover:text-foreground hover:border-primary/30"
                        }`}
                      >
                        {db.label}
                      </button>
                    ))}
                  </div>
                </div>

                {isSqlite ? (
                  <div>
                    <label className="mb-1.5 block text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Database File Path
                    </label>
                    <input
                      type="text"
                      value={config.database}
                      onChange={(e) => updateField("database", e.target.value)}
                      className="w-full rounded-md border border-border bg-input px-3 py-2 font-mono text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                      placeholder="/path/to/database.db"
                    />
                  </div>
                ) : (
                  <>
                    {/* Host & Port */}
                    <div className="grid grid-cols-[1fr_80px] gap-2">
                      <div>
                        <label className="mb-1.5 block text-xs font-medium text-muted-foreground uppercase tracking-wider">
                          Host
                        </label>
                        <input
                          type="text"
                          value={config.host}
                          onChange={(e) => updateField("host", e.target.value)}
                          className="w-full rounded-md border border-border bg-input px-3 py-2 font-mono text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                          placeholder="localhost"
                        />
                      </div>
                      <div>
                        <label className="mb-1.5 block text-xs font-medium text-muted-foreground uppercase tracking-wider">
                          Port
                        </label>
                        <input
                          type="text"
                          value={config.port}
                          onChange={(e) => updateField("port", e.target.value)}
                          className="w-full rounded-md border border-border bg-input px-3 py-2 font-mono text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                          placeholder="5432"
                        />
                      </div>
                    </div>

                    {/* Database */}
                    <div>
                      <label className="mb-1.5 block text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Database Name
                      </label>
                      <input
                        type="text"
                        value={config.database}
                        onChange={(e) => updateField("database", e.target.value)}
                        className="w-full rounded-md border border-border bg-input px-3 py-2 font-mono text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                        placeholder="my_database"
                      />
                    </div>

                    {/* Username */}
                    <div>
                      <label className="mb-1.5 block text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Username
                      </label>
                      <input
                        type="text"
                        value={config.username}
                        onChange={(e) => updateField("username", e.target.value)}
                        className="w-full rounded-md border border-border bg-input px-3 py-2 font-mono text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                        placeholder="postgres"
                      />
                    </div>

                    {/* Password */}
                    <div>
                      <label className="mb-1.5 block text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Password
                      </label>
                      <div className="relative">
                        <input
                          type={showPassword ? "text" : "password"}
                          value={config.password}
                          onChange={(e) => updateField("password", e.target.value)}
                          className="w-full rounded-md border border-border bg-input px-3 py-2 pr-10 font-mono text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                          placeholder="••••••••"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        >
                          {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </button>
                      </div>
                    </div>
                  </>
                )}
                </>
                )}

                {/* Connect / Disconnect */}
                <div className="flex gap-2 pt-2">
                  <button
                    onClick={handleConnect}
                    disabled={isConnecting || (inputMode === "uri" ? !connectionString : !config.database)}
                    className="flex-1 flex items-center justify-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50 disabled:pointer-events-none"
                  >
                    {isConnecting ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Database className="h-4 w-4" />
                    )}
                    {isConnecting ? "Connecting..." : "Connect"}
                  </button>
                  {connectionStatus === "success" && (
                    <button
                      onClick={handleDisconnect}
                      className="rounded-md border border-destructive/50 px-4 py-2.5 text-sm font-medium text-destructive transition-colors hover:bg-destructive/10"
                    >
                      Disconnect
                    </button>
                  )}
                </div>

                {/* Status */}
                <AnimatePresence>
                  {statusMessage && (
                    <motion.div
                      initial={{ opacity: 0, y: -5 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      className={`flex items-start gap-2 rounded-md border p-3 text-xs ${
                        connectionStatus === "success"
                          ? "border-primary/30 bg-primary/5 text-primary"
                          : "border-destructive/30 bg-destructive/5 text-destructive"
                      }`}
                    >
                      {connectionStatus === "success" ? (
                        <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5" />
                      ) : (
                        <XCircle className="h-4 w-4 shrink-0 mt-0.5" />
                      )}
                      <span className="font-mono">{statusMessage}</span>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Info */}
                <div className="rounded-md border border-border bg-muted/50 p-3 mt-2">
                  <p className="text-[10px] text-muted-foreground leading-relaxed">
                    Credentials are sent to your backend at{" "}
                    <span className="font-mono text-accent">{apiBaseUrl}/api/connect</span>{" "}
                    and are never stored in the browser. Your backend handles the actual database connection.
                  </p>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>,
      document.body
      )}
    </>
  );
}
