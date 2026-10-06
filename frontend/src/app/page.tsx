"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { BookOpen, Target, TrendingUp, AlertTriangle } from "lucide-react";

export default function Dashboard() {
  const [studentData, setStudentData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        // Fetch calibration/summary data for our seeded student
        const data = await api.getCalibrationSummary('student_1');
        setStudentData(data);
      } catch (error) {
        console.error("Failed to load dashboard data", error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="max-w-6xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Student Dashboard</h1>
        <p className="text-slate-500 mt-2">Welcome back! Here is an overview of your learning progress.</p>
      </header>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Top Stats Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <StatCard 
              icon={<Target className="text-blue-500" />}
              title="Calibration Status"
              value={studentData?.primary_bias || "Unknown"}
              subtitle="Confidence vs Actual"
            />
            <StatCard 
              icon={<TrendingUp className="text-emerald-500" />}
              title="Actual Mastery"
              value={`${(studentData?.overall_avg_accuracy || 0).toFixed(0)}%`}
              subtitle="Average score"
            />
            <StatCard 
              icon={<BookOpen className="text-indigo-500" />}
              title="Confidence"
              value={`${(studentData?.overall_avg_confidence || 0).toFixed(0)}%`}
              subtitle="Self-reported"
            />
            <StatCard 
              icon={<AlertTriangle className="text-amber-500" />}
              title="Calibration Error"
              value={`${(studentData?.calibration_gap || 0).toFixed(1)}%`}
              subtitle="Difference"
            />
          </div>

          {/* AI Insights Card */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
              <span className="bg-blue-100 text-blue-700 p-2 rounded-lg">✨</span>
              AI Learning Insights
            </h2>
            <div className="bg-slate-50 rounded-lg p-5 border border-slate-100">
              <p className="text-slate-700 text-lg leading-relaxed">
                {studentData?.insight_explanation || "No insights generated yet. Take a quiz to get started."}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ icon, title, value, subtitle }: { icon: React.ReactNode, title: string, value: string, subtitle: string }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 flex flex-col">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
          {icon}
        </div>
        <h3 className="text-sm font-medium text-slate-500">{title}</h3>
      </div>
      <div className="mt-auto">
        <div className="text-3xl font-bold text-slate-900">{value}</div>
        <div className="text-sm text-slate-500 mt-1">{subtitle}</div>
      </div>
    </div>
  );
}
