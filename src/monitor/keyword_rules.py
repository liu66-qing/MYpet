"""关键词匹配规则"""
from dataclasses import dataclass, field


@dataclass
class KeywordRule:
    category: str  # error / success / progress
    keywords: list[str] = field(default_factory=list)


DEFAULT_RULES = [
    KeywordRule("error", [
        "error", "Error", "ERROR",
        "failed", "FAILED", "Failed",
        "exception", "Exception", "EXCEPTION",
        "traceback", "Traceback",
        "fatal", "FATAL",
    ]),
    KeywordRule("success", [
        "completed", "Completed", "COMPLETED",
        "done", "Done", "DONE",
        "finished", "Finished", "FINISHED",
        "success", "Success", "SUCCESS",
        "passed", "Passed", "PASSED",
        "训练完成", "运行结束",
    ]),
    KeywordRule("progress", [
        "epoch", "Epoch",
        "step", "Step",
        "iteration", "Iteration",
        "training", "Training",
        "loss=", "Loss:",
        "accuracy", "Accuracy",
    ]),
]


def match_line(line: str, rules: list[KeywordRule] | None = None) -> tuple[str, str] | None:
    """匹配一行文本，返回 (category, matched_keyword) 或 None"""
    if rules is None:
        rules = DEFAULT_RULES
    for rule in rules:
        for kw in rule.keywords:
            if kw in line:
                return (rule.category, kw)
    return None
