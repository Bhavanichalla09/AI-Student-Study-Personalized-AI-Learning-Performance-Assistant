"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { History, CheckCircle, Clock, Percent, AlertCircle } from "lucide-react";

export default function HistoryPage() {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadHistory() {
      try {
        const data = await api.getLearningHistory("student_1");
        setHistory(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, []);

  return (
    <div className="max-w-5xl mx-auto pb-12">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
          <History className="text-blue-600 h-8 w-8" />
          Learning History
        </h1>
        <p className="text-slate-500 mt-2 text-lg">
          Track your past quiz sessions, diagnostic attempts, and overall accuracy over time.
        </p>
      </header>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : history.length === 0 ? (
        <div className="bg-slate-50 border border-slate-200 rounded-2xl p-12 text-center">
          <div className="w-20 h-20 bg-slate-200 text-slate-400 rounded-full flex items-center justify-center mx-auto mb-4">
            <History className="w-10 h-10" />
          </div>
          <h2 className="text-xl font-bold text-slate-800 mb-2">No History Yet</h2>
          <p className="text-slate-500">Take a practice quiz to see your learning history.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {history.map((session, index) => (
            <div key={session.session_id} className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden transition-all hover:shadow-md">
              <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex justify-between items-center">
                <div>
                  <h3 className="font-bold text-slate-900 text-lg">{session.topic_name}</h3>
                  <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mt-1 flex items-center gap-2">
                    <Clock className="w-4 h-4 text-slate-400" />
                    {session.started_at ? new Date(session.started_at).toLocaleDateString(undefined, {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    }) : "Unknown Date"}
                  </div>
                </div>
                <div>
                  <span className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                    session.status === 'completed' 
                      ? 'bg-emerald-100 text-emerald-700' 
                      : 'bg-amber-100 text-amber-700'
                  }`}>
                    {session.status}
                  </span>
                </div>
              </div>
              
              <div className="p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  {/* Stat 1 */}
                  <div className="flex flex-col">
                    <span className="text-slate-500 text-sm font-medium mb-1">Score</span>
                    <div className="flex items-end gap-2">
                      <span className="text-3xl font-bold text-slate-900">{session.correct_count}</span>
                      <span className="text-slate-400 font-medium mb-1">/ {session.total_questions}</span>
                    </div>
                  </div>

                  {/* Stat 2 */}
                  <div className="flex flex-col">
                    <span className="text-slate-500 text-sm font-medium mb-1">Accuracy</span>
                    <div className="flex items-center gap-2">
                      <span className={`text-2xl font-bold ${
                        session.accuracy_percentage >= 80 ? 'text-emerald-600' : 
                        session.accuracy_percentage >= 50 ? 'text-amber-600' : 'text-rose-600'
                      }`}>
                        {session.accuracy_percentage}%
                      </span>
                      <Percent className="w-4 h-4 text-slate-300" />
                    </div>
                  </div>

                  {/* Stat 3 */}
                  <div className="flex flex-col">
                    <span className="text-slate-500 text-sm font-medium mb-1">Avg Confidence</span>
                    <div className="flex items-center gap-2">
                      <span className="text-2xl font-bold text-blue-600">
                        {session.avg_confidence}%
                      </span>
                    </div>
                  </div>

                  {/* Stat 4 */}
                  <div className="flex flex-col">
                    <span className="text-slate-500 text-sm font-medium mb-1">Calibration Gap</span>
                    <div className="flex items-center gap-2">
                      <span className="text-xl font-bold text-slate-700">
                        {Math.abs(session.avg_confidence - session.accuracy_percentage).toFixed(1)}%
                      </span>
                      {Math.abs(session.avg_confidence - session.accuracy_percentage) > 20 && (
                        <span title="High Calibration Gap">
                          <AlertCircle className="w-5 h-5 text-amber-500" />
                        </span>
                      )}
                    </div>
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
