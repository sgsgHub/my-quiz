import { useEffect, useState } from 'react';
import './App.css';
import {
   getCategories,
   getQuestions,
   createQuizSession,
   getQuizScore,
} from './api';
import type {
   Question,
   CategoriesResponse,
   QuestionsResponse,
   SessionResponse,
   QuizScore,
} from './types';
function App() {
   const [showWelcome, setShowWelcome] = useState(true);
   const [categories, setCategories] = useState<string[]>([]);
   const [shuffledAnswers, setShuffledAnswers] = useState<
      { answer: string; answerId: number }[]
   >([]);
   const [selectedCategory, setSelectedCategory] = useState('');
   const [questions, setQuestions] = useState<Question[]>([]);
   const [sessionId, setSessionId] = useState<number | null>(null);
   const [loading, setLoading] = useState(false);
   const [error, setError] = useState('');
   const [countdown, setCountdown] = useState<number | null>(null);

   const [answerResult, setAnswerResult] = useState<{
      correct: boolean;
      message: string;
      full_answer: string | null;
   } | null>(null);
   const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
   const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
   const [finalScore, setFinalScore] = useState<QuizScore | null>(null);

   function shuffleAnswers(answers: string[]) {
      return answers
         .map((answer, index) => ({ answer, answerId: index + 1 }))
         .sort(() => Math.random() - 0.5);
   }
   function shuffleQuestions(questions: Question[]) {
      return [...questions].sort(() => Math.random() - 0.5);
   }
   function changeCategory() {
      setShowWelcome(true);
      setFinalScore(null);
      setQuestions([]);
      setSessionId(null);
      setCurrentQuestionIndex(0);
      setAnswerResult(null);
      setSelectedCategory('');
   }

   useEffect(() => {
      if (countdown === null) return;

      if (countdown === 0) {
         setCountdown(null);
         handleNextQuestion();
         return;
      }

      const timer = window.setTimeout(() => {
         setCountdown((current) => (current === null ? null : current - 1));
      }, 1000);
      return () => window.clearTimeout(timer);
   }, [countdown]);

   useEffect(() => {
      async function loadCategories() {
         try {
            const data: CategoriesResponse = await getCategories();
            setCategories(data.categories);
         } catch {
            setError('Failed to load categories');
         }
      }

      loadCategories();
   }, []);

   async function startQuiz() {
      setLoading(true);
      setError('');
      setFinalScore(null);
      try {
         const session: SessionResponse = await createQuizSession(
            selectedCategory || undefined,
         );

         const data: QuestionsResponse = await getQuestions(
            selectedCategory || undefined,
         );
         setShowWelcome(false);
         setSessionId(session.session_id);
         const shuffledQuestions = shuffleQuestions(data.questions);

         setQuestions(shuffledQuestions);
         setShuffledAnswers(
            shuffledQuestions.length > 0
               ? shuffleAnswers(shuffledQuestions[0].answers)
               : [],
         );

         setCurrentQuestionIndex(0);
         setAnswerResult(null);
         setSelectedAnswer(null);
      } catch {
         setError('Failed to start quiz');
      } finally {
         setLoading(false);
      }
   }

   async function submitAnswer(answer: number) {
      if (sessionId === null || questions.length === 0) return;

      setError('');

      try {
         const response = await fetch('http://127.0.0.1:8000/quiz/answer', {
            method: 'POST',
            headers: {
               'Content-Type': 'application/json',
            },
            body: JSON.stringify({
               session_id: sessionId,
               question_id: questions[currentQuestionIndex].id,
               answer,
            }),
         });

         if (!response.ok) {
            throw new Error('Failed to submit answer');
         }

         const result = await response.json();

         setSelectedAnswer(answer);
         setAnswerResult(result);
         setCountdown(1);
      } catch {
         setError('Failed to submit answer');
      }
   }
   async function handleNextQuestion() {
      setCountdown(null);
      if (currentQuestionIndex < questions.length - 1) {
         const nextIndex = currentQuestionIndex + 1;

         setCurrentQuestionIndex(nextIndex);
         setShuffledAnswers(shuffleAnswers(questions[nextIndex].answers));
         setAnswerResult(null);
         setSelectedAnswer(null);
         return;
      }

      try {
         const score: QuizScore = await getQuizScore(sessionId!);
         setFinalScore(score);
      } catch {
         setError('Failed to load final score');
      }
   }
   return (
      <main className="app">
         <header className="app-header">
            <div className="logo">Quiz Master</div>
         </header>

         <section className="quiz-container">
            {showWelcome ? (
               <div className="welcome">
                  <h1>Welcome to Quiz Master!</h1>
                  <p>Choose a category and test your knowledge.</p>

                  <select
                     value={selectedCategory}
                     onChange={(event) =>
                        setSelectedCategory(event.target.value)
                     }
                  >
                     <option value="">All categories</option>

                     {categories.map((category) => (
                        <option key={category} value={category}>
                           {category}
                        </option>
                     ))}
                  </select>

                  <button
                     className="primary-button"
                     onClick={startQuiz}
                     disabled={loading}
                  >
                     {loading ? 'Loading...' : 'Start Quiz'}
                  </button>

                  {error && <p className="feedback">{error}</p>}
               </div>
            ) : (
               <div className="quiz-card">
                  {finalScore ? (
                     <div className="welcome">
                        <h2>Quiz Completed!</h2>
                        <p>
                           Your score: {finalScore.score} /{' '}
                           {finalScore.answered}
                        </p>
                        <p>Percentage: {finalScore.percentage}%</p>
                        <button
                           className="primary-button"
                           onClick={startQuiz}
                           disabled={loading}
                        >
                           {loading ? 'Starting...' : 'Play Again'}
                        </button>
                        <button
                           className="primary-button"
                           onClick={changeCategory}
                           disabled={loading}
                        >
                           {loading ? 'Starting...' : 'Change category'}
                        </button>
                     </div>
                  ) : (
                     <>
                        {/* <h2>Quiz started!</h2>
                        <p>Session ID: {sessionId}</p>
                        <p>Questions loaded: {questions.length}</p> */}
                        {answerResult && (
                           <div>
                              {countdown !== null && (
                                 <p>
                                    {currentQuestionIndex < questions.length - 1
                                       ? `Next question in ${countdown} seconds...`
                                       : `Results will appear in ${countdown} seconds...`}
                                 </p>
                              )}
                           </div>
                        )}
                        {questions.length > 0 && (
                           <>
                              <p className="question-category">
                                 {questions[currentQuestionIndex].category}
                              </p>

                              <h2 className="question-title">
                                 {questions[currentQuestionIndex].question}
                              </h2>

                              <div className="answers">
                                 {shuffledAnswers.map(
                                    ({ answer, answerId }) => (
                                       <button
                                          className={`answer-option ${
                                             selectedAnswer === answerId
                                                ? answerResult?.correct
                                                   ? 'correct'
                                                   : answerResult
                                                     ? 'wrong'
                                                     : ''
                                                : ''
                                          }`}
                                          key={answerId}
                                          onClick={() => submitAnswer(answerId)}
                                          disabled={answerResult !== null}
                                       >
                                          {answer}
                                       </button>
                                    ),
                                 )}
                              </div>

                              {answerResult && (
                                 <p className="feedback">
                                    {answerResult.message}
                                    {answerResult.full_answer &&
                                       ` ${answerResult.full_answer}`}
                                 </p>
                              )}

                              {error && <p className="feedback">{error}</p>}
                           </>
                        )}
                     </>
                  )}
               </div>
            )}
         </section>
      </main>
   );
}

export default App;
