"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Compass, CheckCircle2, ArrowRight, Target, BrainCircuit, Activity } from "lucide-react";

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await api.getRecommendations("student_1");
        setRecommendations(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const completeAction = async (id: string) => {
    try {
      await api.completeRecommendation(id);
      setRecommendations(recommendations.filter(r => r.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-5xl mx-auto pb-12">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
          <Compass className="text-blue-600 h-8 w-8" />
          AI Remediation Paths
        </h1>
        <p className="text-slate-500 mt-2 text-lg">
          Personalized learning tasks generated dynamically based on your knowledge map and repeated mistakes.
        </p>
      </header>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : recommendations.length === 0 ? (
        <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-12 text-center">
          <div className="w-20 h-20 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="w-10 h-10" />
          </div>
          <h2 className="text-xl font-bold text-emerald-800 mb-2">You're All Caught Up!</h2>
          <p className="text-emerald-600">Your knowledge map is healthy. Take a new quiz to discover next steps.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {recommendations.map((rec) => (
            <div key={rec.id} className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <span className="bg-blue-100 text-blue-700 p-2 rounded-lg">
                    <Target className="w-5 h-5" />
                  </span>
                  <div>
                    <h3 className="font-bold text-slate-900">{rec.title}</h3>
                    <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mt-1 flex items-center gap-2">
                      <span>Concept: {rec.concept_name}</span>
                      {rec.root_cause_concept_name && (
                        <>
                          <ArrowRight className="w-3 h-3 text-slate-300" />
                          <span className="text-indigo-600">Root Cause: {rec.root_cause_concept_name}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="p-6">
                <div className="flex gap-6 flex-col md:flex-row">
                  {/* Reason */}
                  <div className="flex-1">
                    <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wide mb-3 flex items-center gap-2">
                      <BrainCircuit className="w-4 h-4 text-amber-500" />
                      Why am I seeing this?
                    </h4>
                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 text-slate-700 text-sm leading-relaxed">
                      {rec.reason}
                    </div>
                  </div>
                  
                  {/* Actions */}
                  <div className="flex-1">
                    <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wide mb-3 flex items-center gap-2">
                      <Activity className="w-4 h-4 text-blue-500" />
                      Action Plan
                    </h4>
                    <ul className="space-y-3 mb-6">
                      {rec.action_steps.map((step: string, idx: number) => (
                        <li key={idx} className="flex gap-3 text-sm text-slate-700">
                          <div className="mt-0.5 flex-shrink-0 w-5 h-5 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center font-bold text-xs">
                            {idx + 1}
                          </div>
                          <span className="pt-0.5">{step}</span>
                        </li>
                      ))}
                    </ul>
                    
                    <button 
                      onClick={() => completeAction(rec.id)}
                      className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
                    >
                      <CheckCircle2 className="w-5 h-5" />
                      Mark as Completed
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
