import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SubmitForm } from "./components/SubmitForm/SubmitForm";
import { ResultCard } from "./components/ResultCard/ResultCard";
import { useAnalyze } from "./hooks/useAnalyze";
import "./App.css";

const queryClient = new QueryClient();

function SlopDetector() {
  const { mutate, data, isPending, error } = useAnalyze();

  return (
    <main className="app-main">
      <header className="app-header">
        <h1 className="app-title">AI Slop Detector</h1>
        <p className="app-subtitle">
          Score content 0–100 for signs of low-quality AI generation
        </p>
      </header>

      <div className="app-card">
        <SubmitForm onSubmit={mutate} isLoading={isPending} />
      </div>

      {error && (
        <div className="app-error">
          {error.message}
        </div>
      )}

      {data && <ResultCard result={data} />}
    </main>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SlopDetector />
    </QueryClientProvider>
  );
}
