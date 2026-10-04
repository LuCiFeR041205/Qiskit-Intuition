"""Tests for instant, offline feedback on learner explanations."""
from backend.core.explanation_review import review_explanation
from frontend.learning_content import LESSONS

LESSON = {
    "key_ideas": [
        {"idea": "Repeat many times", "terms": ["shot", "repeat"], "hint": "use many shots."},
        {"idea": "Settles toward 0.75", "terms": ["0.75", "converge"], "hint": "the fraction converges."},
    ],
    "watch_for": [{"terms": ["exactly 75"], "note": "you'll rarely see exactly 75%."}],
}


def test_reports_covered_and_missing_ideas():
    review = review_explanation("With more SHOTS the fraction wobbles less.", LESSON)
    assert [i["idea"] for i in review["covered"]] == ["Repeat many times"]
    assert [i["idea"] for i in review["missing"]] == ["Settles toward 0.75"]
    assert "1 of 2" in review["markdown"] and "the fraction converges." in review["markdown"]


def test_flags_misconceptions_and_handles_empty_text():
    assert review_explanation("It is exactly 75 percent.", LESSON)["flags"]
    assert "Write a few sentences" in review_explanation("   ", LESSON)["markdown"]


def test_short_cues_match_whole_words_only():
    lesson = {"key_ideas": [{"idea": "Mentions H", "terms": ["h"], "hint": "name the gate."}], "watch_for": []}
    assert review_explanation("Then an H gate recombines them.", lesson)["covered"]
    assert not review_explanation("The phase changes.", lesson)["covered"]


def test_complete_answer_gets_a_follow_up_question():
    review = review_explanation("Repeat many shots and the fraction converges to 0.75.", LESSON)
    assert not review["missing"]
    assert "covers the essentials" in review["markdown"]


def test_every_lesson_rubric_is_well_formed():
    for lesson in LESSONS:
        assert len(lesson["key_ideas"]) >= 2, lesson["id"]
        for idea in lesson["key_ideas"]:
            assert idea["idea"] and idea["hint"] and idea["terms"], (lesson["id"], idea)
            assert all(term == term.lower() for term in idea["terms"]), (lesson["id"], idea["terms"])
        for item in lesson["watch_for"]:
            assert item["note"] and all(term == term.lower() for term in item["terms"])


def test_a_model_answer_covers_the_rubric():
    entanglement = next(lesson for lesson in LESSONS if lesson["id"] == "entanglement")
    answer = (
        "The pair has one pure joint state, but each qubit alone is a 50/50 coin: its arrow shrinks to nothing "
        "because the state can't be written as a product of two separate states."
    )
    review = review_explanation(answer, entanglement)
    assert not review["missing"], [i["idea"] for i in review["missing"]]
    assert review_explanation("This lets you send a message faster than light.", entanglement)["flags"]
