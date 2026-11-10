import { useState } from 'react';
import {
   getAdminQuestions,
   getCategories,
   createAdminQuestion,
   updateAdminQuestion,
   deleteAdminQuestion,
   createAdminCategory,
   type AdminQuestion,
   type AdminQuestionInput,
} from './api';
import './AdminPanel.css';

const emptyForm: AdminQuestionInput = {
   category: '',
   question: '',
   full_answer: '',
   correct_answer: 1,
   answers: ['', '', ''],
};

export default function AdminPanel() {
   const [newCategory, setNewCategory] = useState('');
   const [username, setUsername] = useState('');
   const [password, setPassword] = useState('');

   const [questions, setQuestions] = useState<AdminQuestion[]>([]);
   const [categories, setCategories] = useState<string[]>([]);

   const [isAuthenticated, setIsAuthenticated] = useState(false);
   const [loading, setLoading] = useState(false);

   const [editingId, setEditingId] = useState<number | null>(null);
   const [formData, setFormData] = useState<AdminQuestionInput>({
      ...emptyForm,
   });

   const [error, setError] = useState('');
   const [success, setSuccess] = useState('');

   async function loadQuestions() {
      const data = await getAdminQuestions(username, password);
      setQuestions(data.questions);
   }

   async function handleLogin(event: React.SyntheticEvent<HTMLFormElement>) {
      event.preventDefault();

      setLoading(true);
      setError('');

      try {
         const [questionData, categoryData] = await Promise.all([
            getAdminQuestions(username, password),
            getCategories(),
         ]);

         setQuestions(questionData.questions);
         setCategories(categoryData.categories);
         setIsAuthenticated(true);
      } catch (error) {
         setError(error instanceof Error ? error.message : 'Login failed');
      } finally {
         setLoading(false);
      }
   }

   function handleLogout() {
      setUsername('');
      setPassword('');
      setQuestions([]);
      setCategories([]);
      setIsAuthenticated(false);
      setEditingId(null);
      setFormData({ ...emptyForm, answers: ['', '', ''] });
      setError('');
      setSuccess('');
   }

   function handleEdit(question: AdminQuestion) {
      setEditingId(question.id);

      setFormData({
         category: question.category,
         question: question.question,
         full_answer: question.full_answer,
         correct_answer: question.correct_answer,
         answers: [...question.answers],
      });

      setError('');
      setSuccess('');
   }

   function handleCancelEdit() {
      setEditingId(null);
      setFormData({ ...emptyForm, answers: ['', '', ''] });
      setError('');
   }

   async function handleSaveQuestion(
      event: React.SyntheticEvent<HTMLFormElement>,
   ) {
      event.preventDefault();

      setLoading(true);
      setError('');
      setSuccess('');

      try {
         if (editingId !== null) {
            await updateAdminQuestion(username, password, editingId, formData);

            setSuccess('Question updated successfully.');
         } else {
            await createAdminQuestion(username, password, formData);

            setSuccess('Question created successfully.');
         }

         await loadQuestions();

         setEditingId(null);
         setFormData({ ...emptyForm, answers: ['', '', ''] });
      } catch (error) {
         setError(
            error instanceof Error ? error.message : 'Failed to save question',
         );
      } finally {
         setLoading(false);
      }
   }

   async function handleDeleteQuestion(questionId: number) {
      const confirmed = window.confirm(
         `Are you sure you want to delete question #${questionId}?`,
      );

      if (!confirmed) return;

      setLoading(true);
      setError('');
      setSuccess('');

      try {
         await deleteAdminQuestion(username, password, questionId);

         await loadQuestions();

         if (editingId === questionId) {
            handleCancelEdit();
         }

         setSuccess('Question deleted successfully.');
      } catch (error) {
         setError(
            error instanceof Error
               ? error.message
               : 'Failed to delete question',
         );
      } finally {
         setLoading(false);
      }
   }

   async function handleCreateCategory(
      event: React.SyntheticEvent<HTMLFormElement>,
   ) {
      event.preventDefault();

      const name = newCategory.trim();

      if (!name) {
         setError('Category name cannot be empty.');
         return;
      }

      setLoading(true);
      setError('');
      setSuccess('');

      try {
         await createAdminCategory(username, password, name);

         const data = await getCategories();

         setCategories(data.categories);
         setNewCategory('');
         setSuccess('Category created successfully.');
      } catch (error) {
         setError(
            error instanceof Error
               ? error.message
               : 'Failed to create category',
         );
      } finally {
         setLoading(false);
      }
   }

   if (!isAuthenticated) {
      return (
         <section className="admin-panel">
            <h2>Admin Login</h2>

            <form onSubmit={handleLogin}>
               <label htmlFor="admin-username">Username</label>
               <input
                  id="admin-username"
                  type="text"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  required
               />

               <label htmlFor="admin-password">Password</label>
               <input
                  id="admin-password"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
               />

               {error && <p className="admin-error">{error}</p>}

               <button type="submit" disabled={loading}>
                  {loading ? 'Logging in...' : 'Login'}
               </button>
            </form>
         </section>
      );
   }

   return (
      <section className="admin-panel">
         <div className="admin-header">
            <h2>Admin Panel</h2>
            <button onClick={handleLogout}>Logout</button>
         </div>

         <h3>Manage Categories</h3>

         <form className="admin-category-form" onSubmit={handleCreateCategory}>
            <label htmlFor="new-category">New category name</label>

            <input
               id="new-category"
               type="text"
               value={newCategory}
               onChange={(event) => setNewCategory(event.target.value)}
               placeholder="Enter category name"
               required
            />

            <button type="submit" disabled={loading}>
               {loading ? 'Saving...' : 'Add Category'}
            </button>
         </form>

         <h4>Existing categories</h4>

         <ul>
            {categories.map((category) => (
               <li key={category}>{category}</li>
            ))}
         </ul>

         <h3>{editingId !== null ? 'Edit Question' : 'Create Question'}</h3>

         <form className="admin-question-form" onSubmit={handleSaveQuestion}>
            <label htmlFor="question-category">Category</label>

            <select
               id="question-category"
               value={formData.category}
               onChange={(event) =>
                  setFormData({
                     ...formData,
                     category: event.target.value,
                  })
               }
               required
            >
               <option value="">Select category</option>

               {categories.map((category) => (
                  <option key={category} value={category}>
                     {category}
                  </option>
               ))}
            </select>

            <label htmlFor="question-text">Question</label>

            <input
               id="question-text"
               type="text"
               value={formData.question}
               onChange={(event) =>
                  setFormData({
                     ...formData,
                     question: event.target.value,
                  })
               }
               required
            />

            <label htmlFor="full-answer">Full answer</label>

            <input
               id="full-answer"
               type="text"
               value={formData.full_answer}
               onChange={(event) =>
                  setFormData({
                     ...formData,
                     full_answer: event.target.value,
                  })
               }
               required
            />

            <h4>Answer options</h4>

            {formData.answers.map((answer, index) => (
               <div key={index}>
                  <label htmlFor={`answer-${index}`}>Option {index + 1}</label>

                  <input
                     id={`answer-${index}`}
                     type="text"
                     value={answer}
                     onChange={(event) => {
                        const updatedAnswers = [...formData.answers];
                        updatedAnswers[index] = event.target.value;

                        setFormData({
                           ...formData,
                           answers: updatedAnswers,
                        });
                     }}
                     required
                  />
               </div>
            ))}

            <label htmlFor="correct-answer">Correct answer</label>

            <select
               id="correct-answer"
               value={formData.correct_answer}
               onChange={(event) =>
                  setFormData({
                     ...formData,
                     correct_answer: Number(event.target.value),
                  })
               }
            >
               <option value={1}>Option 1</option>
               <option value={2}>Option 2</option>
               <option value={3}>Option 3</option>
            </select>

            <button type="submit" disabled={loading}>
               {loading
                  ? 'Saving...'
                  : editingId !== null
                    ? 'Update Question'
                    : 'Create Question'}
            </button>

            {editingId !== null && (
               <button type="button" onClick={handleCancelEdit}>
                  Cancel Editing
               </button>
            )}
         </form>

         {error && <p className="admin-error">{error}</p>}
         {success && <p className="admin-success">{success}</p>}

         <hr />

         <h3>Questions ({questions.length})</h3>

         {questions.map((question) => (
            <article className="admin-question" key={question.id}>
               <h4>
                  #{question.id} — {question.category}
               </h4>

               <p>{question.question}</p>

               <ul>
                  {question.answers.map((answer, index) => (
                     <li
                        key={index}
                        className={
                           index + 1 === question.correct_answer
                              ? 'correct-answer'
                              : ''
                        }
                     >
                        {answer}
                        {index + 1 === question.correct_answer && ' ✓'}
                     </li>
                  ))}
               </ul>

               <p>
                  <strong>Full answer:</strong> {question.full_answer}
               </p>

               <div className="admin-actions">
                  <button
                     type="button"
                     onClick={() => handleEdit(question)}
                     disabled={loading}
                  >
                     Edit
                  </button>

                  <button
                     type="button"
                     onClick={() => handleDeleteQuestion(question.id)}
                     disabled={loading}
                  >
                     Delete
                  </button>
               </div>
            </article>
         ))}
      </section>
   );
}
