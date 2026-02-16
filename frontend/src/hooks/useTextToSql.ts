import { useState, useEffect } from "react";
import type { TableInfo } from "@/components/SchemaViewer";
import type { SavedQuery } from "@/components/SavedQueries";

export interface QueryHistoryItem {
  id: string;
  naturalQuery: string;
  sqlQuery: string;
  timestamp: Date;
  status: "success" | "error";
  executionTime?: number;
  results?: Record<string, unknown>[];
}

export interface ApiConfig {
  baseUrl: string;
  endpoint: string;
}

const DEFAULT_API_CONFIG: ApiConfig = {
  baseUrl: "http://localhost:8000",
  endpoint: "/api/text-to-sql",
};

export function useTextToSql() {
  const [isLoading, setIsLoading] = useState(false);
  const [sqlOutput, setSqlOutput] = useState("");
  const [results, setResults] = useState<Record<string, unknown>[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<QueryHistoryItem[]>([]);
  const [apiConfig, setApiConfig] = useState<ApiConfig>(DEFAULT_API_CONFIG);
  const [lastNaturalQuery, setLastNaturalQuery] = useState("");
  
  // Connection status
  const [isDbConnected, setIsDbConnected] = useState(false);

  // Schema
  const [schema, setSchema] = useState<TableInfo[]>([]);
  const [isSchemaLoading, setIsSchemaLoading] = useState(false);

  // Explanation
  const [explanation, setExplanation] = useState<string | null>(null);
  const [isExplaining, setIsExplaining] = useState(false);

  // Check connection status on mount and periodically
  useEffect(() => {
    checkConnection();
    // Check connection every 5 seconds
    const interval = setInterval(checkConnection, 5000);
    return () => clearInterval(interval);
  }, [apiConfig.baseUrl]);

  const checkConnection = async () => {
    try {
      const response = await fetch(`${apiConfig.baseUrl}/api/health`);
      if (response.ok) {
        const data = await response.json();
        setIsDbConnected(data.database_connected === true);
      } else {
        setIsDbConnected(false);
      }
    } catch {
      setIsDbConnected(false);
    }
  };

  // Saved queries
  const [savedQueries, setSavedQueries] = useState<SavedQuery[]>(() => {
    try {
      const stored = localStorage.getItem("text2sql_saved_queries");
      if (stored) {
        return JSON.parse(stored).map((q: SavedQuery) => ({
          ...q,
          savedAt: new Date(q.savedAt),
        }));
      }
    } catch {}
    return [];
  });

  const persistSavedQueries = (queries: SavedQuery[]) => {
    setSavedQueries(queries);
    localStorage.setItem("text2sql_saved_queries", JSON.stringify(queries));
  };

  const submitQuery = async (naturalQuery: string) => {
    setIsLoading(true);
    setError(null);
    setSqlOutput("");
    setResults(null);
    setExplanation(null);
    setLastNaturalQuery(naturalQuery);

    try {
      // FIRST: Check if connected to database
      console.log("Checking database connection...");
      const healthResponse = await fetch(`${apiConfig.baseUrl}/api/health`);
      if (!healthResponse.ok) {
        throw new Error("Cannot reach backend");
      }
      
      const health = await healthResponse.json();
      console.log("Health check:", health);
      
      if (!health.database_connected) {
        throw new Error("❌ Please connect to a database first (click the database icon in the header)");
      }
      
      console.log("✅ Database connected, proceeding with query...");

      // THEN: Proceed with the query
      const response = await fetch(`${apiConfig.baseUrl}${apiConfig.endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          query: naturalQuery,
          execute: true,
          limit: 100
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log("API Response:", data);
      
      const sql = data.sql || data.query || data.result || "";
      const queryResults = data.results || data.data || null;
      const execTime = data.execution_time || data.executionTime || undefined;

      setSqlOutput(sql);
      setResults(queryResults);

      const item: QueryHistoryItem = {
        id: crypto.randomUUID(),
        naturalQuery,
        sqlQuery: sql,
        timestamp: new Date(),
        status: "success",
        executionTime: execTime,
        results: queryResults,
      };
      setHistory((prev) => [item, ...prev]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
      console.error("Query error:", message);

      const item: QueryHistoryItem = {
        id: crypto.randomUUID(),
        naturalQuery,
        sqlQuery: "",
        timestamp: new Date(),
        status: "error",
      };
      setHistory((prev) => [item, ...prev]);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSchema = async () => {
    setIsSchemaLoading(true);
    try {
      const response = await fetch(`${apiConfig.baseUrl}/api/schema`);
      if (!response.ok) throw new Error("Failed to fetch schema");
      const data = await response.json();
      setSchema(data.tables || data || []);
    } catch {
      setSchema([]);
    } finally {
      setIsSchemaLoading(false);
    }
  };

  const explainSql = async (sql: string) => {
    setIsExplaining(true);
    try {
      const response = await fetch(`${apiConfig.baseUrl}/api/explain`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sql }),
      });
      if (!response.ok) throw new Error("Failed to explain");
      const data = await response.json();
      setExplanation(data.explanation || data.result || "No explanation available");
    } catch {
      setExplanation("Could not generate explanation. Make sure your backend supports the /api/explain endpoint.");
    } finally {
      setIsExplaining(false);
    }
  };

  const saveQuery = (name: string, naturalQuery: string, sqlQuery: string) => {
    const newQuery: SavedQuery = {
      id: crypto.randomUUID(),
      name,
      naturalQuery,
      sqlQuery,
      savedAt: new Date(),
    };
    persistSavedQueries([newQuery, ...savedQueries]);
  };

  const deleteSavedQuery = (id: string) => {
    persistSavedQueries(savedQueries.filter((q) => q.id !== id));
  };

  return {
    isLoading,
    sqlOutput,
    results,
    error,
    history,
    apiConfig,
    setApiConfig,
    submitQuery,
    setSqlOutput,
    setResults,
    lastNaturalQuery,
    // Connection status
    isDbConnected,
    checkConnection,
    // Schema
    schema,
    isSchemaLoading,
    fetchSchema,
    // Explanation
    explanation,
    isExplaining,
    explainSql,
    // Saved queries
    savedQueries,
    saveQuery,
    deleteSavedQuery,
  };
}