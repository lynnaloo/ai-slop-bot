import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SubmitForm } from "./components/SubmitForm/SubmitForm";
import { ResultCard } from "./components/ResultCard/ResultCard";
import { useAnalyze } from "./hooks/useAnalyze";
import { useAuth } from "./hooks/useAuth";
import { signInWithGoogle, signOutUser } from "./firebase";
import "./App.css";

const queryClient = new QueryClient();

function LoginScreen() {
  return (
    <main className="app-main">
      <header className="app-header">
        <span className="app-eyebrow">🤖 Slop Detector 3000</span>
        <h1 className="app-title">Is it <span>slop</span>?</h1>
        <p className="app-subtitle">
          Sign in with your Salesforce account to start detecting.
        </p>
      </header>
      <div className="app-card" style={{ textAlign: "center" }}>
        <button className="signin-btn" onClick={signInWithGoogle}>
          <GoogleIcon /> Sign in with Google
        </button>
      </div>
    </main>
  );
}

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" style={{ marginRight: 8, verticalAlign: "middle" }}>
      <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z"/>
      <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9 18z"/>
      <path fill="#FBBC05" d="M3.964 10.71c-.18-.54-.282-1.117-.282-1.71s.102-1.17.282-1.71V4.958H.957C.347 6.173 0 7.548 0 9s.348 2.827.957 4.042l3.007-2.332z"/>
      <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.958L3.964 6.29C4.672 4.163 6.656 3.58 9 3.58z"/>
    </svg>
  );
}

function SlopDetector() {
  const { mutate, data, isPending, error, reset } = useAnalyze();
  const { user } = useAuth();

  return (
    <main className="app-main">
      <header className="app-header">
        <span className="app-eyebrow">🤖 Slop Detector 3000</span>
        <h1 className="app-title">Is it <span>slop</span>?</h1>
        <p className="app-subtitle">
          Paste a URL, drop an image, or throw in some text.<br />
          We'll tell you if a robot phoned it in.
        </p>
      </header>

      <div className="app-card">
        <SubmitForm onSubmit={(d) => { reset(); mutate(d); }} isLoading={isPending} />
      </div>

      {error && (
        <div className="app-error">
          {error.message}
        </div>
      )}

      {data && <ResultCard result={data} />}

      <div className="app-user">
        Signed in as {user?.email} &nbsp;·&nbsp;
        <button className="signout-btn" onClick={signOutUser}>Sign out</button>
      </div>
    </main>
  );
}

export default function App() {
  const { user, loading } = useAuth();

  if (loading) return null;

  return (
    <QueryClientProvider client={queryClient}>
      {user ? <SlopDetector /> : <LoginScreen />}
    </QueryClientProvider>
  );
}
