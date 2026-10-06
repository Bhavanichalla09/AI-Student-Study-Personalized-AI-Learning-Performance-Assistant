"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Map, AlertCircle, CheckCircle2, TrendingUp, HelpCircle } from "lucide-react";

export default function KnowledgeMapPage() {
  const [mapData, setMapData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [topics, setTopics] = useState<any[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<string>("topic_func_rec");

  // Load available topics (using the first subject for simplicity)
  useEffect(() => {
    async function init() {
      try {
        const urlParams = new URLSearchParams(window.location.search);
        const urlTopic = urlParams.get('topic_id');
        if (urlTopic) {
          setSelectedTopic(urlTopic);
        }

        const subjects = await api.getSubjects();
        if (subjects.length > 0) {
          const t = await api.getTopics(subjects[0].id);
          setTopics(t);
        }
      } catch (err) {
        console.error("Failed to load subjects/topics", err);
      }
    }
    init();
  }, []);

  useEffect(() => {
    async function loadKnowledgeMap() {
      if (!selectedTopic) return;
      setLoading(true);
      try {
        const data = await api.getKnowledgeMap(selectedTopic, "student_1");
        setMapData(data);
      } catch (error) {
        console.error("Failed to load knowledge map", error);
      } finally {
        setLoading(false);
      }
    }
    loadKnowledgeMap();
  }, [selectedTopic]);

  return (
    <div className="max-w-6xl mx-auto pb-12">
      <header className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
            <Map className="text-blue-600 h-8 w-8" />
            Knowledge Gap Map
          </h1>
          <p className="text-slate-500 mt-2 text-lg">
            Visualize your concept mastery, prerequisites, and learning gaps.
          </p>
        </div>
        <div>
          <select 
            value={selectedTopic} 
            onChange={(e) => setSelectedTopic(e.target.value)}
            className="bg-white border border-slate-300 text-slate-700 font-medium py-2 px-4 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {topics.length > 0 ? topics.map(t => (
              <option key={t.id} value={t.id}>{t.name}</option>
            )) : (
              <option value="topic_func_rec">Functions & Recursion</option>
            )}
          </select>
        </div>
      </header>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : mapData ? (
        <div className="space-y-8">
          {/* Overall Mastery Header */}
          <div className="bg-indigo-600 rounded-xl p-8 text-white flex items-center justify-between shadow-sm">
            <div>
              <h2 className="text-indigo-100 font-medium mb-1">
                Topic: {topics.find(t => t.id === selectedTopic)?.name || "Selected Topic"}
              </h2>
              <div className="text-3xl font-bold">Overall Mastery: {(mapData.overall_mastery * 100).toFixed(0)}%</div>
            </div>
            <div className="w-32 h-32 relative">
              <svg viewBox="0 0 36 36" className="w-full h-full stroke-current">
                <path
                  className="text-indigo-800"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  strokeWidth="3.8"
                />
                <path
                  className="text-indigo-200"
                  strokeDasharray={`${mapData.overall_mastery * 100}, 100`}
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  strokeWidth="3.8"
                />
              </svg>
            </div>
          </div>

          {/* Concepts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {mapData.concepts.map((concept: any) => (
              <ConceptCard key={concept.concept_id} concept={concept} />
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center text-slate-500">Failed to load data.</div>
      )}
    </div>
  );
}

function ConceptCard({ concept }: { concept: any }) {
  const getLevelStyles = (level: string) => {
    switch(level) {
      case 'strong': return 'bg-emerald-50 border-emerald-200 text-emerald-800';
      case 'developing': return 'bg-amber-50 border-amber-200 text-amber-800';
      case 'critical': return 'bg-rose-50 border-rose-200 text-rose-800';
      default: return 'bg-slate-50 border-slate-200 text-slate-800';
    }
  };

  const getLevelIcon = (level: string) => {
    switch(level) {
      case 'strong': return <CheckCircle2 className="text-emerald-500" />;
      case 'developing': return <TrendingUp className="text-amber-500" />;
      case 'critical': return <AlertCircle className="text-rose-500" />;
      default: return <HelpCircle className="text-slate-500" />;
    }
  };

  return (
    <div className={`rounded-xl border shadow-sm overflow-hidden ${getLevelStyles(concept.mastery_level).split(' ')[1]}`}>
      <div className={`px-6 py-4 border-b flex justify-between items-center ${getLevelStyles(concept.mastery_level)}`}>
        <div className="flex items-center gap-3">
          {getLevelIcon(concept.mastery_level)}
          <div>
            <h3 className="font-bold">{concept.concept_name}</h3>
            <span className="text-xs uppercase font-bold tracking-wide opacity-75">{concept.mastery_level}</span>
          </div>
        </div>
        <div className="text-2xl font-bold">
          {(concept.mastery_score * 100).toFixed(0)}%
        </div>
      </div>
      
      <div className="p-6 bg-white space-y-4">
        {/* Progress Bars */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-500">Quiz Accuracy</span>
            <span className="font-medium">{(concept.quiz_accuracy * 100).toFixed(0)}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2">
            <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${concept.quiz_accuracy * 100}%` }}></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-500">Teach-back Score</span>
            <span className="font-medium">{(concept.teachback_score * 100).toFixed(0)}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2">
            <div className="bg-indigo-500 h-2 rounded-full" style={{ width: `${concept.teachback_score * 100}%` }}></div>
          </div>
        </div>

        {/* Prerequisites */}
        {concept.prerequisites && concept.prerequisites.length > 0 && (
          <div className="mt-4 pt-4 border-t border-slate-100">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-2">Depends On</span>
            <div className="flex flex-wrap gap-2">
              {concept.prerequisites.map((prereq: any) => (
                <span key={prereq.concept_id} className="bg-slate-100 text-slate-700 px-2 py-1 rounded text-xs font-medium border border-slate-200">
                  {prereq.concept_name}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
