"use client";

import { ChangeEvent, useState } from "react";

interface Citation {
  document_id: number;
  page_number: number | null;
}

interface ChatResponse {
  answer: string;
  citations: Citation[];
}

interface UploadResponse {
  name: string;
  status: string;
}

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const payload: { detail?: string } = await response.json();
    return payload.detail ?? "The request could not be completed.";
  } catch {
    return "The request could not be completed.";
  }
}

export default function HomePage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [status, setStatus] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleQuestionSubmit() {
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) {
      setStatus("Enter a question before asking the assistant.");
      return;
    }

    setIsSubmitting(true);
    setStatus("Searching your knowledge base…");
    setAnswer("");
    setCitations([]);

    try {
      const response = await fetch("/api/v1/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmedQuestion }),
      });

      if (!response.ok) {
        throw new Error(await getErrorMessage(response));
      }

      const result: ChatResponse = await response.json();
      setAnswer(result.answer);
      setCitations(result.citations ?? []);
      setStatus("");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Unable to reach the API.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleUpload() {
    if (!selectedFile) {
      setStatus("Select a document to upload.");
      return;
    }

    setIsSubmitting(true);
    setStatus("Uploading and indexing your document…");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      const response = await fetch("/api/v1/documents", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await getErrorMessage(response));
      }

      const result: UploadResponse = await response.json();
      setStatus(
        result.status === "ready"
          ? `Indexed: ${result.name}`
          : "The document could not be indexed.",
      );
      setSelectedFile(null);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Unable to reach the API.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    setSelectedFile(event.target.files?.[0] ?? null);
  }

  return (
    <main className="page-content">
      <header className="page-header">
        <h1>Enterprise Knowledge Intelligence Platform</h1>
        <p>Secure enterprise retrieval-augmented generation for your local knowledge base.</p>
      </header>

      <section className="card" aria-labelledby="knowledge-base-heading">
        <h2 id="knowledge-base-heading">Knowledge Base</h2>
        <label className="file-input-label" htmlFor="document-upload">
          Choose a PDF, DOCX, TXT, or Markdown file
        </label>
        <input
          id="document-upload"
          type="file"
          accept=".pdf,.docx,.txt,.md"
          onChange={handleFileChange}
        />
        <button type="button" onClick={handleUpload} disabled={isSubmitting || !selectedFile}>
          Upload and index
        </button>
      </section>

      <section className="card" aria-labelledby="assistant-heading">
        <h2 id="assistant-heading">AI Assistant</h2>
        <label className="visually-hidden" htmlFor="question">
          Question for the assistant
        </label>
        <textarea
          id="question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask a question about your documents…"
        />
        <button type="button" onClick={handleQuestionSubmit} disabled={isSubmitting}>
          Ask assistant
        </button>
      </section>

      {status && <p className="status" role="status">{status}</p>}

      {answer && (
        <section className="answer card" aria-labelledby="answer-heading">
          <h2 id="answer-heading">Answer</h2>
          <p>{answer}</p>
          <h3>Sources</h3>
          {citations.length > 0 ? (
            <ol>
              {citations.map((citation, index) => (
                <li key={`${citation.document_id}-${citation.page_number}-${index}`}>
                  Document #{citation.document_id}
                  {citation.page_number ? ` — page ${citation.page_number}` : ""}
                </li>
              ))}
            </ol>
          ) : (
            <p>No sources were returned.</p>
          )}
        </section>
      )}
    </main>
  );
}
