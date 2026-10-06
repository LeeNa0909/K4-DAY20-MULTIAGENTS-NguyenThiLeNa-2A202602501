"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use before a nontrivial change to inspect documentation, code, "
                "and representative data and report requirements and likely causes."
            ),
            "system_prompt": (
                "You inspect files without changing them. Read the supplied task rules, "
                "README files, docstrings and relevant examples. Report facts with file "
                "references, edge cases and uncertainties. Do not invent requirements. "
                "You see only the delegation message; ask for missing essential context."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use to implement a scoped code repair or data processing task once "
                "the requirements and relevant paths are known."
            ),
            "system_prompt": (
                "Implement only the work specified in the delegation message. Read "
                "the relevant specifications, fix root causes, handle edge cases and "
                "run appropriate tests or validate the generated files. Preserve "
                "unrelated data. Report actual changes, commands, results and remaining "
                "issues. You see only the delegation message."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use after implementation for an independent check of output files, "
                "task requirements, tests and edge cases before declaring completion."
            ),
            "system_prompt": (
                "Review without changing files. Independently compare the actual "
                "outputs with every supplied requirement and relevant documentation. "
                "Run tests or read back outputs to verify claims. Report concrete "
                "failures, evidence and any unverified claims. You see only the "
                "delegation message; do not assume earlier conversations."
            ),
        },
    ]
