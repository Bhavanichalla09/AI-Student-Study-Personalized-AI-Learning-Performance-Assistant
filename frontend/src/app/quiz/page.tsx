"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { BookOpen, CheckCircle, XCircle, AlertCircle, ArrowRight, BrainCircuit } from "lucide-react";

export default function QuizPage() {
  const [quizState, setQuizState] = useState<'idle' | 'loading' | 'active' | 'completed'>('idle');
  const [session, setSession] = useState<any>(null);
  const [questions, setQuestions] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [confidence, setConfidence] = useState<number>(75);
  const [results, setResults] = useState<any[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [topics, setTopics] = useState<any[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<string>("topic_func_rec");

  useEffect(() => {
    async function init() {
      try {
        const urlParams = new URLSearchParams(window.location.search);
        const urlTopic = urlParams.get('topic_id');
        if (urlTopic) setSelectedTopic(urlTopic);

        const subjects = await api.getSubjects();
        if (subjects.length > 0) {
          const t = await api.getTopics(subjects[0].id);
          setTopics(t);
        }
      } catch (err) {
        console.error("Failed to load topics", err);
      }
    }
    init();
  }, []);

  const startQuiz = async () => {
    setQuizState('loading');
    try {
      const data = await api.startQuiz(selectedTopic, "student_1");
      if (!data.questions || data.questions.length === 0) {
        alert("No questions found for this topic.");
        setQuizState('idle');
        return;
      }
      setSession(data.session_id);
      setQuestions(data.questions);
      setQuizState('active');
    } catch (err) {
      console.error(err);
      setQuizState('idle');
    }
  };

  const submitAnswer = async () => {
    if (!selectedOption) return;
    setSubmitting(true);
    
    const currentQ = questions[currentIndex];
    
    try {
      const res = await api.submitAnswer({
        session_id: session,
        question_id: currentQ.id,
        concept_id: currentQ.concept_id,
        selected_option_id: selectedOption,
        confidence_score: confidence,
        time_taken_seconds: 15,
        student_id: "student_1"
      });
      
      setResults(prev => [...prev, res]);
      
      if (currentIndex < questions.length - 1) {
        setCurrentIndex(prev => prev + 1);
        setSelectedOption(null);
        setConfidence(75);
      } else {
        await api.completeQuiz(session);
        setQuizState('completed');
      }
    } catch (err) {
      console.error("Failed to submit", err);
    } finally {
      setSubmitting(false);
    }
  };

  if (quizState === 'idle') {
    return (
      <div className="max-w-4xl mx-auto text-center mt-20">
        <div className="bg-white p-12 rounded-2xl shadow-sm border border-slate-200">
          <BrainCircuit className="w-20 h-20 text-blue-500 mx-auto mb-6" />
          <h1 className="text-3xl font-bold text-slate-900 mb-4">Diagnostic Practice Quiz</h1>
          <p className="text-slate-500 mb-8 max-w-lg mx-auto">
            This quiz isn't just about right or wrong. It measures your confidence and identifies exact misconceptions to build your AI knowledge map.
          </p>
          <div className="flex flex-col items-center gap-4 max-w-xs mx-auto">
            <select 
              value={selectedTopic} 
              onChange={(e) => setSelectedTopic(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 text-slate-700 font-medium py-3 px-4 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {topics.length > 0 ? topics.map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              )) : (
                <option value="topic_func_rec">Functions & Recursion</option>
              )}
            </select>
            <button 
              onClick={startQuiz}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-10 rounded-xl transition-colors shadow-sm"
            >
              Start Diagnostic Quiz
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (quizState === 'loading') {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (quizState === 'completed') {
    const score = results.filter(r => r.is_correct).length;
    return (
      <div className="max-w-3xl mx-auto mt-12">
        <div className="bg-white p-10 rounded-2xl shadow-sm border border-slate-200 text-center">
          <div className="w-24 h-24 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-12 h-12" />
          </div>
          <h2 className="text-3xl font-bold text-slate-900 mb-2">Diagnostic Complete!</h2>
          <p className="text-slate-500 text-lg mb-8">
            You scored {score} out of {questions.length}. Your knowledge map and calibration model have been updated.
          </p>
          <div className="flex justify-center gap-4">
            <a href="/analyzer" className="bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 font-bold py-3 px-6 rounded-lg transition-colors">
              Review Mistakes
            </a>
            <a href={`/knowledge?topic_id=${selectedTopic}`} className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors">
              View Knowledge Map
            </a>
          </div>
        </div>
      </div>
    );
  }

  const currentQ = questions[currentIndex];

  return (
    <div className="max-w-4xl mx-auto pb-12">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between text-sm font-bold text-slate-500 mb-2 uppercase tracking-wide">
          <span>Question {currentIndex + 1} of {questions.length}</span>
          <span>{currentQ.concept_name}</span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all" 
            style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
          ></div>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Question Area */}
        <div className="p-8 border-b border-slate-100">
          <h2 className="text-2xl font-bold text-slate-900">{currentQ.question_text}</h2>
        </div>

        {/* Options */}
        <div className="p-8 bg-slate-50">
          <div className="space-y-4">
            {currentQ.options.map((opt: any) => (
              <label 
                key={opt.id}
                className={`flex items-center p-5 rounded-xl border-2 cursor-pointer transition-all ${
                  selectedOption === opt.id 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-slate-200 bg-white hover:border-blue-300'
                }`}
              >
                <input 
                  type="radio" 
                  name="option" 
                  value={opt.id}
                  checked={selectedOption === opt.id}
                  onChange={() => setSelectedOption(opt.id)}
                  className="w-5 h-5 text-blue-600"
                />
                <span className="ml-4 text-lg font-medium text-slate-800">{opt.text}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Confidence Slider */}
        <div className="p-8 border-t border-slate-100">
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide mb-4 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-500" />
            How confident are you?
          </h3>
          <div className="flex items-center gap-6">
            <span className="text-sm font-medium text-slate-500">Guessing</span>
            <input 
              type="range" 
              min="0" 
              max="100" 
              step="10"
              value={confidence}
              onChange={(e) => setConfidence(parseInt(e.target.value))}
              className="flex-1 h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            <span className="text-sm font-medium text-slate-500">Certain</span>
          </div>
          <div className="text-center mt-2 font-bold text-blue-600">{confidence}%</div>
        </div>

        {/* Submit */}
        <div className="p-6 bg-slate-900 flex justify-end">
          <button 
            onClick={submitAnswer}
            disabled={!selectedOption || submitting}
            className="bg-blue-600 disabled:bg-slate-700 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition-colors flex items-center gap-2"
          >
            {submitting ? 'Submitting...' : currentIndex === questions.length - 1 ? 'Finish Quiz' : 'Next Question'}
            {!submitting && <ArrowRight className="w-5 h-5" />}
          </button>
        </div>
      </div>
    </div>
  );
}
