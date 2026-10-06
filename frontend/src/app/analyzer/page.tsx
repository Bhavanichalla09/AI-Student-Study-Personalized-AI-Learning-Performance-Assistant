"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { BrainCircuit, AlertTriangle, ArrowRight, BookOpen, AlertCircle } from "lucide-react";

export default function AnalyzerPage() {
  const [mistakes, setMistakes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMistakes() {
      try {
        const data = await api.getMistakes("student_1");
        setMistakes(data);
      } catch (error) {
        console.error("Failed to load mistakes", error);
      } finally {
        setLoading(false);
      }
    }
    loadMistakes();
  }, []);

  return (
    <div className="max-w-6xl mx-auto pb-12">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
          <BrainCircuit className="text-blue-600 h-8 w-8" />
          AI Learning Mistake Analyzer
        </h1>
        <p className="text-slate-500 mt-2 text-lg">
          We don't just tell you that you got it wrong. We tell you <strong>why</strong>.
        </p>
      </header>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : mistakes.length === 0 ? (
        <div className="bg-emerald-50 rounded-xl border border-emerald-200 p-12 text-center">
          <h2 className="text-emerald-700 text-xl font-bold mb-2">No Mistakes Found!</h2>
          <p className="text-emerald-600">You are doing great. Keep practicing to build your knowledge map.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {mistakes.map((mistake) => (
            <div key={mistake.id} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              {/* Header */}
              <div className="bg-slate-50 border-b border-slate-200 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                    {mistake.concept_name}
                  </span>
                  {mistake.is_repeated && (
                    <span className="bg-rose-100 text-rose-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1">
                      <AlertCircle size={14} />
                      Repeated {mistake.repeat_count}x
                    </span>
                  )}
                </div>
                <span className="text-sm font-medium text-slate-400">ID: {mistake.id.split('-')[0]}</span>
              </div>

              {/* Question & Answers */}
              <div className="px-6 py-5 grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">The Question</h3>
                  <p className="text-slate-800 text-lg font-medium mb-4">{mistake.question_text}</p>
                  
                  <div className="space-y-3">
                    <div className="bg-rose-50 border border-rose-100 rounded-lg p-3">
                      <span className="text-xs font-bold text-rose-500 uppercase block mb-1">Your Answer (Incorrect)</span>
                      <span className="text-rose-900">{mistake.selected_answer}</span>
                    </div>
                    <div className="bg-emerald-50 border border-emerald-100 rounded-lg p-3">
                      <span className="text-xs font-bold text-emerald-500 uppercase block mb-1">Correct Answer</span>
                      <span className="text-emerald-900">{mistake.correct_answer}</span>
                    </div>
                  </div>
                </div>

                {/* AI Diagnosis */}
                <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-5 flex flex-col justify-center relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-4 opacity-10">
                    <BrainCircuit size={120} />
                  </div>
                  <h3 className="text-sm font-bold text-indigo-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                    <AlertTriangle size={16} />
                    AI Diagnosis
                  </h3>
                  
                  <p className="text-indigo-900 font-medium mb-4 z-10">
                    It looks like you might be struggling with <strong>{mistake.misconception_tag}</strong>.
                  </p>

                  {mistake.root_cause_prerequisite && (
                    <div className="bg-white/60 rounded-lg p-4 z-10 border border-indigo-200">
                      <span className="text-xs font-bold text-indigo-600 block mb-1">Recommended Next Step</span>
                      <p className="text-indigo-900 text-sm flex items-start gap-2">
                        <ArrowRight size={16} className="mt-0.5 flex-shrink-0 text-indigo-500" />
                        <span>
                          Before continuing, you should review the prerequisite concept: 
                          <span className="font-bold ml-1">{mistake.root_cause_prerequisite}</span>
                        </span>
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
