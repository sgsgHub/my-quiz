import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from questions import questions


class QuestionAlreadyAnsweredError(Exception):
    pass


DATABASE_PATH = Path(__file__).parent / "quiz.db"


def is_postgres():
    return bool(os.getenv("DATABASE_URL"))


def get_connection():
    if is_postgres():
        import psycopg
        from psycopg.rows import dict_row

        return psycopg.connect(
            os.environ["DATABASE_URL"],
            sslmode="require",
            prepare_threshold=None,
            row_factory=dict_row,
        )
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def database_connection():
    connection = get_connection()

    try:
        with connection:
            yield connection
    finally:
        connection.close()


def placeholder():
    return "%s" if is_postgres() else "?"


def create_tables():

    if is_postgres():
        raise RuntimeError(
            "create_tables() is for local SQLite only. Supabase tables allready exist"
        )

    connection = get_connection()

    try:
        with connection:
            connection.execute("""
            CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)""")

            connection.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY, category_id INTEGER NOT NULL, question_text TEXT NOT NULL, full_answer TEXT NOT NULL, correct_answer TEXT INTEGER NOT NULL, CHECK (correct_answer BETWEEN 1 AND 3), FOREIGN KEY (category_id) REFERENCES categories(id))

            """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS answer_options (
            question_id INTEGER NOT NULL, option_number INTEGER NOT NULL CHECK (option_number BETWEEN 1 AND 3), answer_text TEXT NOT NULL, PRIMARY KEY (question_id, option_number), FOREIGN KEY (question_id) REFERENCES questions(id))        

                            """)
        connection.execute("""
                CREATE TABLE IF NOT EXISTS quiz_sessions (
                    id INTEGER PRIMARY KEY,
                    category_id INTEGER,
                    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id)
                        REFERENCES categories(id)
                )
            """)
        columns = connection.execute("PRAGMA table_info(quiz_sessions)").fetchall()

        column_names = [column["name"] for column in columns]

        if "status" not in column_names:
            connection.execute("""
                ALTER TABLE quiz_sessions
                ADD COLUMN status TEXT NOT NULL
                DEFAULT 'in_progress'
                CHECK (status IN ('in_progress', 'completed'))
                                """)
        connection.execute("""
                CREATE TABLE IF NOT EXISTS quiz_results (
                    id INTEGER PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    selected_answer INTEGER NOT NULL
                        CHECK (selected_answer BETWEEN 1 AND 3),
                    is_correct INTEGER NOT NULL
                        CHECK (is_correct IN (0, 1)),
                    answered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id)
                        REFERENCES quiz_sessions(id),
                    FOREIGN KEY (question_id)
                        REFERENCES questions(id),
                    UNIQUE (session_id, question_id)
                )
            """)

    finally:
        connection.close()


def seed_questions():

    if is_postgres():
        raise RuntimeError(
            "seed_questions() is for local SQLite only. "
            "Supabase already contains the quiz questions."
        )

    connection = get_connection()

    try:
        with connection:
            for item in questions:
                connection.execute(
                    """
                    INSERT INTO categories (name)
                    VALUES (?) ON CONFLICT(name) DO NOTHING
                    """,
                    (item["category"],),
                )

                category_id = connection.execute(
                    "SELECT id FROM categories WHERE name = ?",
                    (item["category"],),
                ).fetchone()["id"]

                existing_question = connection.execute(
                    """
                    SELECT id FROM questions WHERE category_id = ? AND  question_text = ?
                    """,
                    (category_id, item["question"]),
                ).fetchone()

                if existing_question:
                    continue

                cursor = connection.execute(
                    """
                    INSERT INTO questions ( category_id, question_text, full_answer, correct_answer) VALUES (?, ?, ?, ?)
                    """,
                    (
                        category_id,
                        item["question"],
                        item["full_answer"],
                        item["correct_answer"],
                    ),
                )
                question_id = cursor.lastrowid

                for number, answer in enumerate(item["answers"], start=1):
                    connection.execute(
                        """
                    INSERT INTO answer_options(
                    question_id, option_number, answer_text) VALUES (?, ?, ?)
                        """,
                        (question_id, number, answer),
                    )
    finally:
        connection.close()


def get_categories_from_db():
    with database_connection() as connection:
        rows = connection.execute(
            "SELECT name FROM categories ORDER BY name"
        ).fetchall()

        return [row["name"] for row in rows]


def get_questions_from_db(category=None):
    placeholder_value = placeholder()

    query = """
            SELECT
                questions.id,
                categories.name AS category,
                questions.question_text,
                questions.full_answer,
                questions.correct_answer
            FROM questions
            JOIN categories
                ON questions.category_id = categories.id
        """
    parameters = ()

    if category is not None:
        query += f" WHERE categories.name = {placeholder_value}"
        parameters = (category,)

    query += " ORDER BY questions.id"

    with database_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()
        result = []

        for row in rows:
            options = connection.execute(
                f"""
                SELECT option_number, answer_text
                FROM answer_options
                WHERE question_id = {placeholder_value}
                ORDER BY option_number
                """,
                (row["id"],),
            ).fetchall()

            result.append(
                {
                    "id": row["id"],
                    "category": row["category"],
                    "question": row["question_text"],
                    "full_answer": row["full_answer"],
                    "correct_answer": row["correct_answer"],
                    "answers": [option["answer_text"] for option in options],
                }
            )

        return result


def get_question_from_db(question_id):
    placeholder_value = placeholder()

    with database_connection() as connection:
        row = connection.execute(
            f"""
            SELECT
                questions.id,
                categories.name AS category,
                questions.question_text,
                questions.full_answer,
                questions.correct_answer
            FROM questions
            JOIN categories
                ON questions.category_id = categories.id
            WHERE questions.id = {placeholder_value}
            """,
            (question_id,),
        ).fetchone()

        if row is None:
            return None

        options = connection.execute(
            f"""
            SELECT answer_text
            FROM answer_options
            WHERE question_id = {placeholder_value}
            ORDER BY option_number
            """,
            (question_id,),
        ).fetchall()

        return {
            "id": row["id"],
            "category": row["category"],
            "question": row["question_text"],
            "full_answer": row["full_answer"],
            "correct_answer": row["correct_answer"],
            "answers": [option["answer_text"] for option in options],
        }


def create_quiz_session(category=None):
    placeholder_value = placeholder()

    with database_connection() as connection:
        category_id = None

        if category is not None:
            row = connection.execute(
                f"SELECT id FROM categories WHERE name = {placeholder_value}",
                (category,),
            ).fetchone()

            if row is None:
                raise ValueError(f"Unknown category: {category}")

            category_id = row["id"]

        if is_postgres():
            cursor = connection.execute(
                """
                INSERT INTO quiz_sessions (category_id)
                VALUES (%s)
                RETURNING id
                """,
                (category_id,),
            )
            return cursor.fetchone()["id"]

        cursor = connection.execute(
            """
            INSERT INTO quiz_sessions (category_id)
            VALUES (?)
            """,
            (category_id,),
        )
        return cursor.lastrowid


def save_quiz_answer(session_id, question_id, selected_answer):
    if selected_answer not in (1, 2, 3):
        raise ValueError("Answer must be between 1 and 3")

    placeholder_value = placeholder()

    with database_connection() as connection:
        session = connection.execute(
            f"SELECT id, category_id, status FROM quiz_sessions WHERE id = {placeholder_value}",
            (session_id,),
        ).fetchone()

        if session is None:
            raise ValueError(f"Unknown session ID: {session_id}")
        if session["status"] == "completed":
            raise ValueError("This quiz session is already completed")
        existing_result = connection.execute(
            f"""
                SELECT id
                FROM quiz_results
                WHERE session_id = {placeholder_value} AND question_id = {placeholder_value}
                """,
            (session_id, question_id),
        ).fetchone()
        if existing_result is not None:
            raise QuestionAlreadyAnsweredError(
                "This question has already been answered in this session"
            )
        question = connection.execute(
            f"""
                SELECT category_id, correct_answer
                FROM questions
                WHERE id = {placeholder_value}
                """,
            (question_id,),
        ).fetchone()

        if question is None:
            raise ValueError(f"Unknown question ID: {question_id}")
        if (
            session["category_id"] is not None
            and session["category_id"] != question["category_id"]
        ):
            raise ValueError("Question does not belong to this session's category")
        is_correct = selected_answer == question["correct_answer"]

        connection.execute(
            f"""
                INSERT INTO quiz_results (
                    session_id,
                    question_id,
                    selected_answer,
                    is_correct
                )
                VALUES ({placeholder_value}, {placeholder_value}, {placeholder_value}, {placeholder_value})
                """,
            (
                session_id,
                question_id,
                selected_answer,
                is_correct,
            ),
        )
        if session["category_id"] is None:
            total_row = connection.execute(
                "SELECT COUNT(*) AS total FROM questions"
            ).fetchone()
        else:
            total_row = connection.execute(
                f"""
                SELECT COUNT(*) AS total
                FROM questions
                WHERE category_id = {placeholder_value}
                """,
                (session["category_id"],),
            ).fetchone()

        answered_row = connection.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM quiz_results
            WHERE session_id = {placeholder_value}
            """,
            (session_id,),
        ).fetchone()

        total_questions = total_row["total"]
        answered_questions = answered_row["total"]

        if answered_questions == total_questions:
            connection.execute(
                f"""
                UPDATE quiz_sessions
                SET status = 'completed'
                WHERE id = {placeholder_value}
                """,
                (session_id,),
            )

        return {
            "session_id": session_id,
            "question_id": question_id,
            "correct": is_correct,
        }


def get_quiz_score(session_id):
    placeholder_value = placeholder()
    with database_connection() as connection:
        session = connection.execute(
            f"SELECT id, status FROM quiz_sessions WHERE id = {placeholder_value}",
            (session_id,),
        ).fetchone()

        if session is None:
            raise ValueError(f"Unknown session ID: {session_id}")

        result = connection.execute(
            f"""
            SELECT
                COUNT(*) AS answered,
                COALESCE(
                SUM(CASE WHEN is_correct THEN 1 ELSE 0 END),
                0
                ) AS score
            FROM quiz_results
            WHERE session_id = {placeholder_value}
            """,
            (session_id,),
        ).fetchone()

        answered = result["answered"]
        score = result["score"]
        percentage = round(score / answered * 100) if answered else 0

        return {
            "status": session["status"],
            "session_id": session_id,
            "answered": answered,
            "score": score,
            "percentage": percentage,
        }
