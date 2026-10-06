// Central API Client for FastAPI Backend Communication
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

async function fetchJson<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    let errorDetail = 'Unknown API Error';
    try {
      const errData = await response.json();
      errorDetail = errData.detail || errData.message || JSON.stringify(errData);
    } catch {
      errorDetail = await response.text();
    }
    throw new Error(errorDetail || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  // Health
  checkHealth: () => fetchJson<{ status: string; environment: string }>('/health'),

  // Curriculum & Concepts
  getSubjects: () => fetchJson<any[]>('/subjects'),
  getTopics: (subjectId: string) => fetchJson<any[]>(`/subjects/${subjectId}/topics`),
  getConcepts: (topicId: string) => fetchJson<any[]>(`/topics/${topicId}/concepts`),
  getGraph: (topicId: string) => fetchJson<any>(`/graph/${topicId}`),
  getPrerequisites: (conceptId: string) => fetchJson<any>(`/prerequisites/${conceptId}`),

  // Quiz & Assessment
  startQuiz: (topicId: string, studentId?: string) =>
    fetchJson<any>('/quiz/start', {
      method: 'POST',
      body: JSON.stringify({ topic_id: topicId, student_id: studentId }),
    }),
  submitAnswer: (submission: any) =>
    fetchJson<any>('/quiz/submit-answer', {
      method: 'POST',
      body: JSON.stringify(submission),
    }),
  completeQuiz: (sessionId: string) =>
    fetchJson<any>(`/quiz/complete/${sessionId}`, { method: 'POST' }),
  getQuizResults: (sessionId: string) => fetchJson<any>(`/quiz/session/${sessionId}`),

  // Mistakes
  getMistakes: (studentId?: string) =>
    fetchJson<any[]>(`/mistakes${studentId ? `?student_id=${studentId}` : ''}`),
  getMistakeDetails: (mistakeId: string) => fetchJson<any>(`/mistakes/${mistakeId}`),

  // Knowledge Gap Map
  getKnowledgeMap: (topicId: string, studentId?: string) =>
    fetchJson<any>(`/learner/knowledge-map/${topicId}${studentId ? `?student_id=${studentId}` : ''}`),
  getConceptDiagnosis: (conceptId: string, studentId?: string) =>
    fetchJson<any>(`/learner/concept-diagnosis/${conceptId}${studentId ? `?student_id=${studentId}` : ''}`),

  // Teach-Back
  submitTeachBack: (conceptId: string, explanation: string, studentId?: string) =>
    fetchJson<any>('/teachback/evaluate', {
      method: 'POST',
      body: JSON.stringify({
        concept_id: conceptId,
        student_explanation: explanation,
        student_id: studentId,
      }),
    }),
  getTeachBackHistory: (conceptId: string, studentId?: string) =>
    fetchJson<any[]>(`/teachback/history/${conceptId}${studentId ? `?student_id=${studentId}` : ''}`),

  // Confidence & Calibration
  getCalibrationSummary: (studentId?: string) =>
    fetchJson<any>(`/confidence/summary${studentId ? `?student_id=${studentId}` : ''}`),

  // Recommendations & Remediation
  getRecommendations: (studentId?: string) =>
    fetchJson<any[]>(`/recommendations${studentId ? `?student_id=${studentId}` : ''}`),
  completeRecommendation: (recommendationId: string) =>
    fetchJson<any>(`/recommendations/${recommendationId}/complete`, { method: 'POST' }),

  // History & Retest
  getLearningHistory: (studentId?: string) =>
    fetchJson<any>(`/history${studentId ? `?student_id=${studentId}` : ''}`),
  retestConcept: (conceptId: string, studentId?: string) =>
    fetchJson<any>('/quiz/retest', {
      method: 'POST',
      body: JSON.stringify({ concept_id: conceptId, student_id: studentId }),
    }),
};
