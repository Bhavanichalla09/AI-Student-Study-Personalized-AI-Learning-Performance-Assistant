"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { MessageSquare, Send, CheckCircle2, AlertCircle, RefreshCw } from "lucide-react";

export default function TeachBackPage() {
  const [conceptId, setConceptId] = useState("concept_variables");
  const [explanation, setExplanation] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<any>(null);

  const handleSubmit = async () => {
    if (!explanation.trim()) return;
    setSubmitting(true);
    try {
      const result = await api.submitTeachBack(conceptId, explanation, "student_1");
      setFeedback(result);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto pb-12">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
          <MessageSquare className="text-blue-600 h-8 w-8" />
          AI Teach-Back Evaluator
        </h1>
        <p className="text-slate-500 mt-2 text-lg">
          To truly learn something, you must be able to teach it. Explain a concept below, and our AI will evaluate your understanding.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Left Side: Input area */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col h-[500px]">
          <div className="mb-4">
            <label className="block text-sm font-bold text-slate-700 mb-2">Select Concept to Explain</label>
            <select 
              value={conceptId}
              onChange={(e) => {
                setConceptId(e.target.value);
                setFeedback(null);
                setExplanation("");
              }}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="concept_variables">Python Variables</option>
              <option value="concept_loops">Python Loops (For/While)</option>
              <option value="concept_functions">Python Functions</option>
            </select>
          </div>

          <div className="flex-1 flex flex-col">
            <label className="block text-sm font-bold text-slate-700 mb-2">Your Explanation</label>
            <textarea 
              value={explanation}
              onChange={(e) => setExplanation(e.target.value)}
              placeholder="Explain it like I am 5 years old..."
              className="w-full flex-1 bg-slate-50 border border-slate-200 rounded-lg p-4 resize-none text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>

          <div className="mt-4 pt-4 border-t border-slate-100 flex justify-end">
            <button 
              onClick={handleSubmit}
              disabled={submitting || !explanation.trim()}
              className="bg-blue-600 disabled:bg-slate-400 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors flex items-center gap-2"
            >
              {submitting ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
              {submitting ? "Evaluating..." : "Submit Explanation"}
            </button>
          </div>
        </div>

        {/* Right Side: AI Feedback */}
        <div className="bg-slate-50 rounded-2xl shadow-inner border border-slate-200 p-6 flex flex-col">
          {!feedback ? (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-400 text-center p-8">
              <MessageSquare className="w-16 h-16 mb-4 opacity-50" />
              <p>Submit your explanation to get AI-powered feedback on your conceptual understanding.</p>
            </div>
          ) : (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="flex items-center gap-4">
                <div className={`p-4 rounded-full ${feedback.score >= 0.8 ? 'bg-emerald-100 text-emerald-600' : feedback.score >= 0.5 ? 'bg-amber-100 text-amber-600' : 'bg-rose-100 text-rose-600'}`}>
                  <span className="text-2xl font-bold">{(feedback.score * 100).toFixed(0)}%</span>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900">Evaluation Complete</h3>
                  <p className="text-slate-500">{feedback.score >= 0.8 ? 'Great explanation!' : 'Needs some work.'}</p>
                </div>
              </div>

              <div className="bg-white rounded-xl p-5 border border-slate-200">
                <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" /> AI Feedback
                </h4>
                <p className="text-slate-800 leading-relaxed">{feedback.feedback}</p>
              </div>

              {feedback.missed_key_points && feedback.missed_key_points.length > 0 && (
                <div className="bg-rose-50 rounded-xl p-5 border border-rose-100">
                  <h4 className="text-sm font-bold text-rose-600 uppercase tracking-wide mb-3 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" /> Missed Key Points
                  </h4>
                  <ul className="space-y-2">
                    {feedback.missed_key_points.map((point: string, idx: number) => (
                      <li key={idx} className="flex gap-2 text-rose-800 text-sm">
                        <span className="mt-1 flex-shrink-0 bg-rose-200 rounded-full w-4 h-4 flex items-center justify-center text-[10px] font-bold">{idx + 1}</span>
                        {point}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {feedback.misconceptions_detected && feedback.misconceptions_detected.length > 0 && (
                <div className="bg-amber-50 rounded-xl p-5 border border-amber-100">
                  <h4 className="text-sm font-bold text-amber-600 uppercase tracking-wide mb-3 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" /> Misconceptions Detected
                  </h4>
                  <ul className="space-y-2">
                    {feedback.misconceptions_detected.map((m: string, idx: number) => (
                      <li key={idx} className="flex gap-2 text-amber-800 text-sm font-medium">
                        • {m}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
