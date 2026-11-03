def get_categories(questions):
    return sorted({question["category"] for question in questions})


def get_questions_by_category(questions, category):
    return [question for question in questions if question["category"] == category]


def check_answer(user_answer, correct_answer):
    return user_answer == correct_answer


def calculate_score(results):
    return sum(results)


def calculate_percentage(score, total_questions):
    if total_questions == 0:
        return 0
    return round(score / total_questions * 100)
