const API_URL = 'http://127.0.0.1:8000';

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

export async function getQuizScore(sessionId: number) {
   const response = await fetch(`${API_URL}/quiz/session/${sessionId}/score`);

   if (!response.ok) {
      throw new Error('Failed to load quiz score');
   }

   return response.json();
}
