"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { BookOpen, Folder, FileText, ChevronRight, ChevronDown, Network } from "lucide-react";

export default function CurriculumPage() {
  const [subjects, setSubjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedSubject, setExpandedSubject] = useState<string | null>(null);
  const [topics, setTopics] = useState<Record<string, any[]>>({});
  const [expandedTopic, setExpandedTopic] = useState<string | null>(null);
  const [concepts, setConcepts] = useState<Record<string, any[]>>({});

  useEffect(() => {
    async function loadSubjects() {
      try {
        const data = await api.getSubjects();
        setSubjects(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadSubjects();
  }, []);

  const toggleSubject = async (subjectId: string) => {
    if (expandedSubject === subjectId) {
      setExpandedSubject(null);
      return;
    }
    setExpandedSubject(subjectId);
    if (!topics[subjectId]) {
      try {
        const data = await api.getTopics(subjectId);
        setTopics(prev => ({ ...prev, [subjectId]: data }));
      } catch (err) {
        console.error(err);
      }
    }
  };

  const toggleTopic = async (topicId: string) => {
    if (expandedTopic === topicId) {
      setExpandedTopic(null);
      return;
    }
    setExpandedTopic(topicId);
    if (!concepts[topicId]) {
      try {
        const data = await api.getConcepts(topicId);
        setConcepts(prev => ({ ...prev, [topicId]: data }));
      } catch (err) {
        console.error(err);
      }
    }
  };

  return (
    <div className="max-w-5xl mx-auto pb-12">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
          <BookOpen className="text-blue-600 h-8 w-8" />
          Curriculum Explorer
        </h1>
        <p className="text-slate-500 mt-2 text-lg">
          Browse the complete knowledge architecture. Discover subjects, topics, and underlying concepts.
        </p>
      </header>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {subjects.map(subject => (
            <div key={subject.id} className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden transition-all">
              {/* Subject Header */}
              <button 
                onClick={() => toggleSubject(subject.id)}
                className="w-full px-6 py-5 flex items-center justify-between hover:bg-slate-50 transition-colors text-left"
              >
                <div className="flex items-center gap-4">
                  <div className={`p-2 rounded-lg ${expandedSubject === subject.id ? 'bg-blue-100 text-blue-600' : 'bg-slate-100 text-slate-500'}`}>
                    <BookOpen className="w-6 h-6" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-slate-900">{subject.name}</h2>
                    <p className="text-slate-500 text-sm">{subject.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium text-slate-400 bg-slate-100 px-3 py-1 rounded-full">
                    {subject.topics_count} Topics
                  </span>
                  {expandedSubject === subject.id ? <ChevronDown className="text-slate-400" /> : <ChevronRight className="text-slate-400" />}
                </div>
              </button>

              {/* Topics List */}
              {expandedSubject === subject.id && (
                <div className="border-t border-slate-100 bg-slate-50 px-6 py-4">
                  {topics[subject.id] ? (
                    <div className="space-y-3">
                      {topics[subject.id].map(topic => (
                        <div key={topic.id} className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
                          <button 
                            onClick={() => toggleTopic(topic.id)}
                            className="w-full px-5 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors text-left"
                          >
                            <div className="flex items-center gap-3">
                              <Folder className="w-5 h-5 text-indigo-500" />
                              <span className="font-bold text-slate-800">{topic.name}</span>
                            </div>
                            <div className="flex items-center gap-4">
                              <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                                {topic.concepts_count} Concepts
                              </span>
                              <div className="flex gap-2 mr-2">
                                <a href={`/quiz?topic_id=${topic.id}`} className="text-xs bg-indigo-100 text-indigo-700 hover:bg-indigo-200 px-3 py-1.5 rounded-md font-medium transition-colors" onClick={(e) => e.stopPropagation()}>
                                  Start Quiz
                                </a>
                                <a href={`/knowledge?topic_id=${topic.id}`} className="text-xs bg-slate-200 text-slate-700 hover:bg-slate-300 px-3 py-1.5 rounded-md font-medium transition-colors" onClick={(e) => e.stopPropagation()}>
                                  View Map
                                </a>
                              </div>
                              {expandedTopic === topic.id ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                            </div>
                          </button>

                          {/* Concepts List */}
                          {expandedTopic === topic.id && (
                            <div className="border-t border-slate-100 px-5 py-4 bg-slate-50/50">
                              {concepts[topic.id] ? (
                                <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                  {concepts[topic.id].map((concept: any) => (
                                    <li key={concept.id} className="flex items-start gap-3 p-3 bg-white border border-slate-100 rounded-lg hover:border-blue-300 transition-colors group">
                                      <FileText className="w-4 h-4 text-slate-400 mt-0.5 group-hover:text-blue-500" />
                                      <div>
                                        <div className="font-medium text-slate-800 text-sm group-hover:text-blue-700">{concept.name}</div>
                                        <div className="text-xs text-slate-400 font-mono mt-1">{concept.code}</div>
                                      </div>
                                    </li>
                                  ))}
                                </ul>
                              ) : (
                                <div className="text-center text-sm text-slate-400 py-4">Loading concepts...</div>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center text-slate-400 py-6">Loading topics...</div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
