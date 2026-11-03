export interface Question {
   id: number;
   category: string;
   question: string;
   answers: string[];
}

export interface CategoriesResponse {
   categories: string[];
}

export interface QuestionsResponse {
   questions: Question[];
}

export interface SessionResponse {
   session_id: number;
}

export interface QuizScore {
   session_id: number;
   score: number;
   answered: number;
   percentage: number;
   status: string;
}
