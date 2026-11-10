import type { QuizScore } from './types';

const API_URL = (
   import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
).replace(/\/$/, '');

export type AdminQuestion = {
   id: number;
   category: string;
   question: string;
   full_answer: string;
   correct_answer: number;
   answers: string[];
};

export type AdminQuestionInput = {
   category: string;
   question: string;
   full_answer: string;
   correct_answer: number;
   answers: string[];
};

function getAdminHeaders(username: string, password: string) {
   const credentials = btoa(
      Array.from(new TextEncoder().encode(`${username}:${password}`), (byte) =>
         String.fromCharCode(byte),
      ).join(''),
   );

   return {
      Authorization: `Basic ${credentials}`,
   };
}

export type CategoriesResponse = {
   categories: string[];
};

export type AdminCategory = {
   id: number;
   name: string;
};

export type AdminCategoriesResponse = {
   categories: AdminCategory[];
};

export type QuestionsResponse = {
   questions: {
      id: number;
      category: string;
      question: string;
      answers: string[];
   }[];
};

export type SessionResponse = {
   session_id: number;
};

export type AnswerResult = {
   correct: boolean;
   message: string;
   full_answer: string | null;
};

async function handleResponse<T>(
   response: Response,
   fallbackMessage: string,
): Promise<T> {
   if (!response.ok) {
      let message = fallbackMessage;

      try {
         const data = await response.json();
         message = data.detail || fallbackMessage;
      } catch {
         // Keep the fallback message.
      }

      throw new Error(message);
   }

   return response.json();
}

// Existing quiz API functions

export async function getCategories(): Promise<CategoriesResponse> {
   const response = await fetch(`${API_URL}/categories`);

   return handleResponse(response, 'Failed to load categories');
}

export async function getQuestions(
   category?: string,
): Promise<QuestionsResponse> {
   const url = category
      ? `${API_URL}/questions?category=${encodeURIComponent(category)}`
      : `${API_URL}/questions`;

   const response = await fetch(url);

   return handleResponse(response, 'Failed to load questions');
}

export async function createQuizSession(
   category?: string,
): Promise<SessionResponse> {
   const response = await fetch(`${API_URL}/quiz/session/`, {
      method: 'POST',
      headers: {
         'Content-Type': 'application/json',
      },
      body: JSON.stringify({ category: category ?? null }),
   });

   return handleResponse(response, 'Failed to create quiz session');
}

export async function submitQuizAnswer(
   sessionId: number,
   questionId: number,
   answer: number,
): Promise<AnswerResult> {
   const response = await fetch(`${API_URL}/quiz/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
         session_id: sessionId,
         question_id: questionId,
         answer,
      }),
   });

   return handleResponse(response, 'Failed to submit answer');
}

export async function getQuizScore(sessionId: number): Promise<QuizScore> {
   const response = await fetch(`${API_URL}/quiz/session/${sessionId}/score`);

   return handleResponse(response, 'Failed to load quiz score');
}

// Admin API functions

export async function getAdminQuestions(
   username: string,
   password: string,
): Promise<{ questions: AdminQuestion[] }> {
   const response = await fetch(`${API_URL}/admin/questions`, {
      headers: getAdminHeaders(username, password),
      cache: 'no-store',
   });

   return handleResponse(response, 'Failed to load admin questions');
}
export async function getAdminCategories(
   username: string,
   password: string,
): Promise<AdminCategoriesResponse> {
   const response = await fetch(`${API_URL}/admin/categories`, {
      headers: getAdminHeaders(username, password),
      cache: 'no-store',
   });

   return handleResponse(response, 'Failed to load admin categories');
}
export async function createAdminQuestion(
   username: string,
   password: string,
   question: AdminQuestionInput,
) {
   const response = await fetch(`${API_URL}/admin/questions`, {
      method: 'POST',
      headers: {
         ...getAdminHeaders(username, password),
         'Content-Type': 'application/json',
      },
      body: JSON.stringify(question),
   });

   return handleResponse(response, 'Failed to create question');
}

export async function updateAdminQuestion(
   username: string,
   password: string,
   questionId: number,
   question: AdminQuestionInput,
) {
   const response = await fetch(`${API_URL}/admin/questions/${questionId}`, {
      method: 'PUT',
      headers: {
         ...getAdminHeaders(username, password),
         'Content-Type': 'application/json',
      },
      body: JSON.stringify(question),
   });

   return handleResponse(response, 'Failed to update question');
}

export async function deleteAdminQuestion(
   username: string,
   password: string,
   questionId: number,
) {
   const response = await fetch(`${API_URL}/admin/questions/${questionId}`, {
      method: 'DELETE',
      headers: getAdminHeaders(username, password),
   });

   return handleResponse(response, 'Failed to delete question');
}

export async function createAdminCategory(
   username: string,
   password: string,
   name: string,
) {
   const response = await fetch(`${API_URL}/admin/categories`, {
      method: 'POST',
      headers: {
         ...getAdminHeaders(username, password),
         'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name }),
   });

   return handleResponse(response, 'Failed to create category');
}

export async function updateAdminCategory(
   username: string,
   password: string,
   categoryId: number,
   name: string,
) {
   const response = await fetch(`${API_URL}/admin/categories/${categoryId}`, {
      method: 'PUT',
      headers: {
         ...getAdminHeaders(username, password),
         'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name }),
   });

   return handleResponse(response, 'Failed to update category');
}

export async function deleteAdminCategory(
   username: string,
   password: string,
   categoryId: number,
) {
   const response = await fetch(`${API_URL}/admin/categories/${categoryId}`, {
      method: 'DELETE',
      headers: getAdminHeaders(username, password),
   });

   return handleResponse(response, 'Failed to delete category');
}
