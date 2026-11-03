import random
import time

from game_logic import (
    calculate_percentage,
    calculate_score,
    check_answer,
    get_categories,
    get_questions_by_category,
)
from questions import questions
from validate_questions import validate_questions


def choose_category(questions):
    categories = ["All categories"] + get_categories(questions)

    print("\n Choose a category:")

    for number, category in enumerate(categories, start=1):
        print(f"{number}. {category}")

    while True:
        choice = input("Your choice:")

        if choice.isdigit():
            choice = int(choice)

            if 1 <= choice <= len(categories):
                return categories[choice - 1]
        print(f"Mistake! Type number from 1 to {len(categories)}")


def get_valid_answer():
    while True:
        user_answer = input("Your answer (1-3): ")

        if user_answer.isdigit() and 1 <= int(user_answer) <= 3:
            return int(user_answer)
        print("Mistake! Type number from 1 to 3")


def ask_question(item, question_number):
    print(item["question"])

    for number, answer in enumerate(item["answers"], start=1):
        print(f"{number}. {answer}")

    user_answer = get_valid_answer()
    if check_answer(user_answer, item["correct_answer"]):
        print("Correct!")
        return True
    else:
        print("Wrong!")
        print(f"{item['full_answer']}")
        return False


def main():
    while True:
        validate_questions(questions)
        results = []

        print("\n=== Our quiz ===")

        category = choose_category(questions)
        if category == "All categories":
            selected_questions = questions
        else:
            selected_questions = get_questions_by_category(questions, category)
        selected_questions = selected_questions.copy()
        random.shuffle(selected_questions)
        results = []
        for question_number, item in enumerate(selected_questions, start=1):
            print(f"\nQuestion {question_number} of {len(selected_questions)}")
            show_progress(question_number - 1, len(selected_questions))
            result = ask_question(item, question_number)
            results.append(result)
            time.sleep(1)
        score = calculate_score(results)
        total_questions = len(selected_questions)
        percentage = calculate_percentage(score, total_questions)
        print("\nGame over!")
        print(f"Your result: {score} of {total_questions}")

        print(f"Correct answers {percentage}%")

        if not ask_to_play_again():
            print("Thanks for playing!")
            break


def ask_to_play_again():
    while True:
        answer = input("\nPlay again? (y/n): ").strip().lower()

        if answer in ("y", "n"):
            return answer == "y"

        print("Please enter 'y' of 'n'. ")


def show_progress(current, total):
    percentage = round(current / total * 100)
    filled = round(percentage / 10)
    bar = "#" * filled + "." * (10 - filled)

    print(f"Progress: [{bar}]{percentage}%")


if __name__ == "__main__":
    main()
