def validate_questions(questions):
    if not questions:
        raise ValueError("List of questions is empty")
    for number, item in enumerate(questions, start=1):
        if "question" not in item:
            raise ValueError(f"Question N{number}: text of question is absent")
        if "answers" not in item:
            raise ValueError(f"Question N{number}: variants of answers are absent")
        if len(item["answers"]) != 3:
            raise ValueError(f"Question N{number}: variants of answers have to be 3")

        correct_answer = item.get("correct_answer")

        if not isinstance(correct_answer, int) or isinstance(correct_answer, bool):
            raise TypeError(f"Question N{number}: number of answer has to be integer")

        if not 1 <= correct_answer <= 3:
            raise ValueError(
                f"Question N{number}: correct answer has to have number from 1 to 3"
            )
        if not isinstance(item["question"], str) or not item["question"].strip():
            raise ValueError(f"Question N{number}: text can't be empty")
        if not all(
            isinstance(answer, str) and answer.strip() for answer in item["answers"]
        ):
            raise ValueError(f"Question №{number}: all variants have to contain text.")

        category = item.get("category")
        if not isinstance(category, str) or not category.strip():
            raise ValueError(
                f"Question N{number}: the category can't be an empty string."
            )
    return True
