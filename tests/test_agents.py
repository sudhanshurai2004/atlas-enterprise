from app.agents.critic_agent import critique_answer


def test_critic_rejects_weak_answer() -> None:
    result = critique_answer(
        {"answer": "Unsupported", "citations": [], "confidence": 0.4}
    )

    assert result["approved"] is False
    assert "Low confidence" in result["feedback"][0]
    assert result["rounds_remaining"] == 1


def test_critic_approves_supported_answer() -> None:
    result = critique_answer(
        {
            "answer": "Supported",
            "citations": [{"title": "Runbook"}],
            "confidence": 0.9,
        }
    )

    assert result["approved"] is True
