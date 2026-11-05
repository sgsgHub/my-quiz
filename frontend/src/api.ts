// Set VITE_API_URL in Vercel to the deployed API origin, for example
// https://your-api.example.com. The localhost default is for local development.
const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

export async function getCategories() {
   const response = await fetch(`${API_URL}/categories`);

   if (!response.ok) {
      throw new Error('Failed to load categories');
   }

   return response.json();
}

export async function getQuestions(category?: string) {
   const url = category
      ? `${API_URL}/questions?category=${encodeURIComponent(category)}`
      : `${API_URL}/questions`;

   const response = await fetch(url);

   if (!response.ok) {
      throw new Error('Failed to load questions');
   }

   return response.json();
}

export async function createQuizSession(category?: string) {
   const response = await fetch(`${API_URL}/quiz/session/`, {
      method: 'POST',
      headers: {
         'Content-Type': 'application/json',
      },
      body: JSON.stringify({ category: category ?? null }),
   });

   if (!response.ok) {
      throw new Error('Failed to create quiz session');
   }

   return response.json();
}

export async function submitQuizAnswer(
   sessionId: number,
   questionId: number,
   answer: number,
) {
   const response = await fetch(`${API_URL}/quiz/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
         session_id: sessionId,
         question_id: questionId,
         answer,
      }),
   });

   if (!response.ok) {
      throw new Error('Failed to submit answer');
   }

   return response.json();
}

export async function getQuizScore(sessionId: number) {
   const response = await fetch(`${API_URL}/quiz/session/${sessionId}/score`);

   if (!response.ok) {
      throw new Error('Failed to load quiz score');
   }

   return response.json();
}
