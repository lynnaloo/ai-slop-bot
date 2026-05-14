import { useState, useRef, type FormEvent } from "react";
import type { AnalyzeFormData, InputType } from "../../types/api";
import "./SubmitForm.css";

interface Props {
  onSubmit: (data: AnalyzeFormData) => void;
  isLoading: boolean;
}

const TABS: { id: InputType; label: string }[] = [
  { id: "url", label: "URL" },
  { id: "image", label: "Image" },
  { id: "text", label: "Text" },
];

export function SubmitForm({ onSubmit, isLoading }: Props) {
  const [tab, setTab] = useState<InputType>("url");
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (tab === "url") onSubmit({ input_type: "url", url });
    else if (tab === "text") onSubmit({ input_type: "text", text });
    else if (tab === "image" && imageFile) onSubmit({ input_type: "image", image: imageFile });
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file?.type.startsWith("image/")) setImageFile(file);
  }

  const canSubmit =
    !isLoading &&
    ((tab === "url" && url.trim()) ||
      (tab === "text" && text.trim()) ||
      (tab === "image" && imageFile));

  return (
    <form className="submit-form" onSubmit={handleSubmit}>
      <div className="tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            className={`tab ${tab === t.id ? "tab--active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "url" && (
        <input
          className="input-field"
          type="url"
          placeholder="https://example.com/article"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />
      )}

      {tab === "text" && (
        <textarea
          className="input-field input-textarea"
          placeholder="Paste the text you want to check for AI slop..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={8}
          required
        />
      )}

      {tab === "image" && (
        <div
          className={`dropzone ${dragOver ? "dropzone--over" : ""}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileRef.current?.click()}
        >
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            className="dropzone-input"
            onChange={(e) => setImageFile(e.target.files?.[0] ?? null)}
          />
          {imageFile ? (
            <p className="dropzone-name">{imageFile.name}</p>
          ) : (
            <p>Drop an image here or click to browse</p>
          )}
        </div>
      )}

      <button className="submit-btn" type="submit" disabled={!canSubmit}>
        {isLoading ? "Analyzing…" : "Check for Slop"}
      </button>
    </form>
  );
}
