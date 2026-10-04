"""Tests for the tester feedback form's issue filing."""
from urllib.parse import parse_qs, urlparse

import requests

from backend.core import feedback

CONTEXT = {"page": "Learning path", "lesson": "3. Measurement and shots", "stage": "Predict"}


def test_report_carries_the_message_and_where_it_came_from():
    report = feedback.build_report("Bug", "The histogram never updates\nwhen I change shots.", CONTEXT)
    assert report["title"] == "[Feedback] Bug: The histogram never updates (3. Measurement and shots)"
    assert report["body"].startswith("The histogram never updates")
    assert "- **Stage:** Predict" in report["body"]


def test_validation_rejects_empty_and_huge_messages():
    assert feedback.validate("   ") is not None
    assert feedback.validate("x" * (feedback.MAX_LENGTH + 1)) is not None
    assert feedback.validate("This step was confusing.") is None


def test_without_a_token_the_tester_gets_a_prefilled_issue_link(monkeypatch):
    monkeypatch.delenv("FEEDBACK_GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("FEEDBACK_GITHUB_REPO", raising=False)
    report = feedback.build_report("Idea", "Add a lesson on the quantum Fourier transform.", CONTEXT)
    result = feedback.submit(report)
    assert result["status"] == "link"
    url = urlparse(result["url"])
    assert url.path == f"/{feedback.DEFAULT_REPO}/issues/new"
    assert parse_qs(url.query)["title"] == [report["title"]]


def test_with_a_token_the_issue_is_filed(monkeypatch):
    calls = {}

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"html_url": "https://github.com/owner/repo/issues/7"}

    def fake_post(url, json, headers, timeout):
        calls.update(url=url, json=json, auth=headers["Authorization"])
        return Response()

    monkeypatch.setenv("FEEDBACK_GITHUB_TOKEN", "secret")
    monkeypatch.setenv("FEEDBACK_GITHUB_REPO", "owner/repo")
    monkeypatch.setattr(feedback.requests, "post", fake_post)
    result = feedback.submit(feedback.build_report("Bug", "Sphere doesn't drag on my tablet.", CONTEXT))
    assert result == {"status": "filed", "url": "https://github.com/owner/repo/issues/7"}
    assert calls["url"] == "https://api.github.com/repos/owner/repo/issues"
    assert calls["auth"] == "Bearer secret"


def test_a_failed_post_falls_back_to_the_link(monkeypatch):
    def failing_post(*args, **kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setenv("FEEDBACK_GITHUB_TOKEN", "secret")
    monkeypatch.setattr(feedback.requests, "post", failing_post)
    result = feedback.submit(feedback.build_report("Bug", "Something went wrong here.", CONTEXT))
    assert result["status"] == "link" and result["error"] == "ConnectionError"
