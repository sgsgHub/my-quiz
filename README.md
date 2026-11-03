# README --- учебный проект «Графическая викторина»

> Этот файл фиксирует доступную на момент создания сводку обсуждения и
> состояние проекта. Он не обновляется автоматически при каждом новом
> сообщении: после важных этапов попросите ChatGPT обновить README.md.

## 1. Цель проекта

Создать графическую викторину для Windows и параллельно изучать Python
на реальном проекте --- от простой консольной версии к графическому
приложению.

### Подтверждённые требования

-   В каждом вопросе ровно 3 варианта ответа.
-   Ровно 1 вариант правильный.
-   За правильный ответ начисляется 1 очко.
-   Некорректный ввод не должен пропускать вопрос: программа должна
    запросить ответ повторно.
-   Планируются графический интерфейс и анимации.
-   Сами вопросы не должны становиться сложнее; со временем варианты
    ответа могут становиться более похожими.

## 2. Среда разработки

Использовать указанные версии без обновления, если пользователь отдельно
не согласует изменение:

-   Python 3.12.10
-   Node.js v24.14.1
-   npm 11.11.0

Рабочая среда: Windows, Visual Studio Code, PowerShell.

Пользователь знаком с основами JavaScript и React, а Python изучает
через практику.

## 3. Правила сопровождения проекта

1.  Учитывать историю проекта и ранее принятые решения.
2.  Не менять согласованные технологии, архитектуру и требования без
    предварительного обсуждения.
3.  Различать подтверждённые факты, решения, предложения и
    предположения.
4.  Не заявлять, что задача выполнена, пока результат не проверен.
5.  Перед существенными изменениями сверяться с предыдущими решениями.
6.  Если контекста недостаточно, задать один конкретный уточняющий
    вопрос.
7.  Учитывать существующую структуру и не переписывать работающие части
    без необходимости.
8.  После значимого этапа обновлять статус проекта.
9.  Не предлагать обновлять версии инструментов без обсуждения.
10. README --- контрольная точка проекта; просить обновить его после
    значимых изменений.

## 4. Предполагаемая будущая архитектура

Ранее обсуждалась как возможный вариант, но не должна считаться
окончательно утверждённой без подтверждения пользователя:

-   Python + FastAPI --- backend;
-   React + TypeScript --- frontend;
-   CSS и Motion for React --- стили и анимации;
-   SQLite --- локальная база данных;
-   Electron --- оболочка Windows-приложения;
-   PyInstaller --- возможная упаковка backend.

До отдельного согласования не считать этот список окончательным
архитектурным решением.

## 5. Текущий учебный прототип

Предполагаемая структура файлов:

``` text
quiz-master/
├── .venv/
├── main.py
├── questions.py
├── validate_questions.py
└── tests/
    ├── test_validate_questions.py
    └── test_game_logic.py
```

**Статус:** код ниже был подготовлен в ходе обучения, но создание файлов
и успешный запуск не подтверждены. Сначала проверить фактическое
состояние файлов и результаты тестов.

### `questions.py`

``` python
questions = [
    {
        "question": "Какой язык мы используем для игровой логики?",
        "answers": ["Java", "Python", "PHP"],
        "correct_answer": 2,
    },
    {
        "question": "Какой язык используется вместе с React?",
        "answers": ["TypeScript", "SQL", "Bash"],
        "correct_answer": 1,
    },
    {
        "question": "Как называется библиотека для создания интерфейсов?",
        "answers": ["Django", "React", "FastAPI"],
        "correct_answer": 2,
    },
]
```

Нумерация правильных ответов начинается с 1.

### `validate_questions.py`

``` python
def validate_questions(questions):
    if not questions:
        raise ValueError("Список вопросов пуст.")

    for number, item in enumerate(questions, start=1):
        if "question" not in item:
            raise ValueError(f"Вопрос №{number}: отсутствует текст вопроса.")

        if "answers" not in item:
            raise ValueError(f"Вопрос №{number}: отсутствуют варианты ответа.")

        if len(item["answers"]) != 3:
            raise ValueError(
                f"Вопрос №{number}: должно быть ровно 3 варианта ответа."
            )

        correct_answer = item.get("correct_answer")

        if not isinstance(correct_answer, int) or isinstance(correct_answer, bool):
            raise ValueError(
                f"Вопрос №{number}: номер правильного ответа должен быть целым числом."
            )

        if not 1 <= correct_answer <= 3:
            raise ValueError(
                f"Вопрос №{number}: правильный ответ должен иметь номер от 1 до 3."
            )

        if not isinstance(item["question"], str) or not item["question"].strip():
            raise ValueError(f"Вопрос №{number}: текст не должен быть пустым.")

        if not all(
            isinstance(answer, str) and answer.strip()
            for answer in item["answers"]
        ):
            raise ValueError(
                f"Вопрос №{number}: все варианты должны содержать текст."
            )

    return True
```

### `main.py`

``` python
from questions import questions
from validate_questions import validate_questions


def get_valid_answer():
    while True:
        user_answer = input("Твой ответ (1-3): ")

        if user_answer.isdigit() and 1 <= int(user_answer) <= 3:
            return int(user_answer)

        print("Ошибка! Введи число от 1 до 3.")


def check_answer(user_answer, correct_answer):
    return user_answer == correct_answer


def ask_question(item, question_number):
    print(f"\\nВопрос {question_number}:")
    print(item["question"])

    for number, answer in enumerate(item["answers"], start=1):
        print(f"{number}. {answer}")

    user_answer = get_valid_answer()

    if check_answer(user_answer, item["correct_answer"]):
        print("Правильно!")
        return True

    print("Неправильно!")
    return False


def calculate_score(results):
    return sum(results)


def main():
    validate_questions(questions)
    results = []

    print("\\n=== Наша викторина ===")

    for question_number, item in enumerate(questions, start=1):
        result = ask_question(item, question_number)
        results.append(result)

    score = calculate_score(results)

    print(
        f"\\nИгра завершена! "
        f"Твой результат: {score} из {len(questions)}"
    )


if __name__ == "__main__":
    main()
```

### `tests/test_validate_questions.py`

``` python
import unittest

from validate_questions import validate_questions


class TestValidateQuestions(unittest.TestCase):

    def test_valid_question(self):
        questions = [
            {
                "question": "Какой язык мы изучаем?",
                "answers": ["Java", "Python", "PHP"],
                "correct_answer": 2,
            }
        ]

        self.assertTrue(validate_questions(questions))

    def test_empty_questions(self):
        with self.assertRaises(ValueError):
            validate_questions([])

    def test_wrong_number_of_answers(self):
        questions = [
            {
                "question": "Тестовый вопрос",
                "answers": ["A", "B"],
                "correct_answer": 1,
            }
        ]

        with self.assertRaises(ValueError):
            validate_questions(questions)

    def test_invalid_correct_answer(self):
        questions = [
            {
                "question": "Тестовый вопрос",
                "answers": ["A", "B", "C"],
                "correct_answer": 4,
            }
        ]

        with self.assertRaises(ValueError):
            validate_questions(questions)


if __name__ == "__main__":
    unittest.main()
```

### `tests/test_game_logic.py`

``` python
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
from io import StringIO

from main import check_answer, ask_question, calculate_score


class TestGameLogic(unittest.TestCase):

    def test_correct_answer(self):
        self.assertTrue(check_answer(2, 2))

    def test_wrong_answer(self):
        self.assertFalse(check_answer(1, 2))

    def test_ask_question_returns_true_for_correct_answer(self):
        item = {
            "question": "Какой язык мы изучаем?",
            "answers": ["Java", "Python", "PHP"],
            "correct_answer": 2,
        }

        with patch("builtins.input", return_value="2"):
            with redirect_stdout(StringIO()):
                result = ask_question(item, 1)

        self.assertTrue(result)

    def test_ask_question_returns_false_for_wrong_answer(self):
        item = {
            "question": "Какой язык мы изучаем?",
            "answers": ["Java", "Python", "PHP"],
            "correct_answer": 2,
        }

        with patch("builtins.input", return_value="1"):
            with redirect_stdout(StringIO()):
                result = ask_question(item, 1)

        self.assertFalse(result)

    def test_calculate_score_all_correct(self):
        self.assertEqual(calculate_score([True, True, True]), 3)

    def test_calculate_score_some_correct(self):
        self.assertEqual(calculate_score([True, False, True]), 2)

    def test_calculate_score_none_correct(self):
        self.assertEqual(calculate_score([False, False, False]), 0)


if __name__ == "__main__":
    unittest.main()
```

Ожидание по этим тестам: 4 теста валидации и 7 тестов игровой логики,
всего 11. Это ожидаемое количество, а не подтверждённый результат
запуска.

## 6. Изученные темы Python

По ходу обучения разбирались:

-   переменные, списки и словари;
-   `print()` и `input()`;
-   `if` / `else`, циклы `for` и `while`, `break`;
-   `enumerate(..., start=1)`;
-   методы `.isdigit()` и преобразование `int()`;
-   логический оператор `and`;
-   функции `def`, параметры и `return`;
-   значения `True` и `False`;
-   `sum()` и `.append()`;
-   импорты `from ... import ...`;
-   точка входа `if __name__ == "__main__":`;
-   исключения `raise ValueError`;
-   словарный метод `.get()` и проверка типов `isinstance()`;
-   базовые тесты `unittest`: `assertTrue`, `assertFalse`,
    `assertEqual`, `assertRaises`;
-   изоляция ввода и вывода в тестах через `patch`, `redirect_stdout` и
    `StringIO`.

## 7. Следующие шаги

1.  Проверить, какие файлы уже созданы в VS Code.

2.  Запустить консольную игру и убедиться, что она работает.

3.  Запустить тесты из корневой папки проекта:

    ``` powershell
    python -m unittest discover -s tests -v
    ```

4.  Если запуск не проходит, сначала исправить конкретную ошибку, не
    переписывая проект целиком.

5.  Добавить тест на некорректный ввод (например, `0`, `4`, буквы) и
    проверить, что программа повторно запрашивает ответ.

6.  После проверки обновить этот README: указать фактические результаты,
    изменённые файлы и следующий этап.

7.  Продолжать двигаться от консольной версии к графическому интерфейсу,
    не меняя архитектуру без обсуждения.

## 8. Как поддерживать README актуальным

README не может сам по себе автоматически записывать новые сообщения
чата. После значимого этапа напишите:

**«Обнови README.md по текущему состоянию проекта. Сохрани принятые
решения, изученные темы, изменения файлов, проверенные результаты и
следующий шаг. Не записывай непроверенное как выполненное».**

Если нужно перенести работу в новый чат, используйте запрос:

**«Прочитай README.md и продолжи проект с указанного следующего шага,
соблюдая правила сопровождения».**

## 9. Текущий статус

-   **Цель:** создать графическую викторину для Windows и изучать Python
    на практике.
-   **Текущий этап:** консольный учебный прототип с валидацией вопросов
    и модульными тестами.
-   **Проверено фактически:** по доступной истории запуск файлов и
    тестов не подтверждён.
-   **Основной риск:** не считать предложенный код и структуру
    созданными или работающими, пока пользователь не проверит их в своей
    среде.
-   **Следующий шаг:** проверить реальные файлы и выполнить запуск игры
    и тестов.
