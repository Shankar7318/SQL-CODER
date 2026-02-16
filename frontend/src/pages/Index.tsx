import { Database, Terminal } from "lucide-react";
import { QueryInput } from "@/components/QueryInput";
import { SqlOutput } from "@/components/SqlOutput";
import { ResultsTable } from "@/components/ResultsTable";
import { QueryHistory } from "@/components/QueryHistory";
import { SettingsPanel } from "@/components/SettingsPanel";
import { SchemaViewer } from "@/components/SchemaViewer";
import { ExportButton } from "@/components/ExportButton";
import { SqlExplanation } from "@/components/SQLExplanation";
import { SavedQueries } from "@/components/SavedQueries";
import { QueryStats } from "@/components/QueryStats";
import { DatabaseConnection } from "@/components/DatabaseConnection";
import { useTextToSql } from "@/hooks/useTextToSql";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const Index = () => {
  const {
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
    schema,
    isSchemaLoading,
    fetchSchema,
    explanation,
    isExplaining,
    explainSql,
    savedQueries,
    saveQuery,
    deleteSavedQuery,
  } = useTextToSql();

  const handleHistorySelect = (item: { sqlQuery: string; results?: Record<string, unknown>[] }) => {
    setSqlOutput(item.sqlQuery);
    setResults(item.results || null);
  };

  const handleTableClick = (tableName: string) => {
    submitQuery(`Show all records from ${tableName}`);
  };

  const handleRunSaved = (query: { naturalQuery: string; sqlQuery: string }) => {
    submitQuery(query.naturalQuery);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-30">
        <div className="container flex h-14 items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 glow-primary">
              <Database className="h-4 w-4 text-primary" />
            </div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold tracking-tight text-foreground">
                Text2SQL
              </h1>
              <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-mono uppercase tracking-widest text-primary">
                SQLCoder
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ExportButton results={results} sql={sqlOutput} />
            <DatabaseConnection
              apiBaseUrl={apiConfig.baseUrl}
              onConnected={() => fetchSchema()}
            />
            <div className="flex items-center gap-1.5 rounded-md border border-border bg-muted/50 px-2.5 py-1">
              <Terminal className="h-3 w-3 text-muted-foreground" />
              <span className="text-[10px] font-mono text-muted-foreground">
                {apiConfig.baseUrl}
              </span>
            </div>
            <SettingsPanel config={apiConfig} onChange={setApiConfig} />
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container py-6">
        {/* Stats Bar */}
        <QueryStats history={history} />

        <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_300px]">
          <div className="space-y-6">
            {/* Query Input */}
            <section>
              <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Natural Language Query
              </label>
              <QueryInput onSubmit={submitQuery} isLoading={isLoading} />
            </section>

            {/* SQL Output */}
            <section>
              <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Generated SQL
              </label>
              <SqlOutput sql={sqlOutput} error={error} isLoading={isLoading} />
            </section>

            {/* SQL Explanation */}
            <section>
              <SqlExplanation
                sql={sqlOutput}
                explanation={explanation}
                isLoading={isExplaining}
                onExplain={explainSql}
              />
            </section>

            {/* Results */}
            <section>
              <ResultsTable results={results} />
            </section>
          </div>

          {/* Sidebar */}
          <aside className="space-y-4">
            <Tabs defaultValue="history" className="w-full">
              <TabsList className="w-full grid grid-cols-3 bg-muted/50">
                <TabsTrigger value="history" className="text-xs">History</TabsTrigger>
                <TabsTrigger value="saved" className="text-xs">Saved</TabsTrigger>
                <TabsTrigger value="schema" className="text-xs">Schema</TabsTrigger>
              </TabsList>
              <TabsContent value="history" className="mt-3">
                <QueryHistory history={history} onSelect={handleHistorySelect} />
              </TabsContent>
              <TabsContent value="saved" className="mt-3">
                <SavedQueries
                  savedQueries={savedQueries}
                  onSave={saveQuery}
                  onDelete={deleteSavedQuery}
                  onRun={handleRunSaved}
                  currentNaturalQuery={lastNaturalQuery}
                  currentSql={sqlOutput}
                />
              </TabsContent>
              <TabsContent value="schema" className="mt-3">
                <SchemaViewer
                  tables={schema}
                  isLoading={isSchemaLoading}
                  onRefresh={fetchSchema}
                  onTableClick={handleTableClick}
                />
              </TabsContent>
            </Tabs>
          </aside>
        </div>
      </main>
    </div>
  );
};

export default Index;
