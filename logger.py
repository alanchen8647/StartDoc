"""
Logging system for DocuBot FAQ helper.

Tracks:
1. Guardrail blocks (SSN/EIN/names)
2. Retrieval misses (queries below threshold)
3. Query-answer pairs (for evaluation)
4. User feedback (helpful/not helpful)

Future: These logs will be reviewed to improve the system.
"""

import json
import os
from datetime import datetime
from typing import Optional, List


class FAQLogger:
    """Simple file-based logger for FAQ queries and results."""

    def __init__(self, log_dir: str = "."):
        """
        Initialize logger.

        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = log_dir
        self.guardrail_log = os.path.join(log_dir, "guardrail_blocks.jsonl")
        self.retrieval_log = os.path.join(log_dir, "retrieval_results.jsonl")
        self.feedback_log = os.path.join(log_dir, "user_feedback.jsonl")

    def log_guardrail_block(self, reason: str, query_preview: str = "") -> None:
        """
        Log when a query is blocked by guardrails.

        Args:
            reason: Why it was blocked (SSN, EIN, Name detected)
            query_preview: First 50 chars of query (for context, no PII)
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "event": "guardrail_block",
            "reason": reason,
            "query_preview": query_preview[:50] if query_preview else "",
        }
        self._append_log(self.guardrail_log, record)
        print(f"[LOG] Guardrail block: {reason}")

    def log_retrieval_miss(self, query: str, reason: str = "score too low") -> None:
        """
        Log when retrieval returns no results.

        Args:
            query: The original query
            reason: Why it was rejected (e.g., "score: 2.5 < 3.0")
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "event": "retrieval_miss",
            "query": query,
            "reason": reason,
        }
        self._append_log(self.retrieval_log, record)

    def log_retrieval_hit(self, query: str, filename: str, score: float) -> None:
        """
        Log successful retrieval.

        Args:
            query: The original query
            filename: Which document was retrieved
            score: The relevance score
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "event": "retrieval_hit",
            "query": query,
            "filename": filename,
            "score": score,
        }
        self._append_log(self.retrieval_log, record)

    def log_answer(self,
                   query: str,
                   answer: str,
                   source: str,
                   mode: str = "retrieval") -> None:
        """
        Log a question and the answer provided.

        Args:
            query: The staff member's question
            answer: The system's answer
            source: Where answer came from (e.g., "fee_cover_page_2026.md")
            mode: "retrieval" (no LLM) or "rag" (with LLM)
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "event": "answer_provided",
            "query": query,
            "answer": answer[:200],  # First 200 chars
            "source": source,
            "mode": mode,
        }
        self._append_log(self.retrieval_log, record)

    def log_user_feedback(self, query: str, answer: str, helpful: bool, notes: str = "") -> None:
        """
        Log user feedback on answer quality.

        Args:
            query: The original query
            answer: What system said
            helpful: Whether user found it helpful
            notes: Optional notes from user
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "event": "user_feedback",
            "query": query,
            "answer": answer[:200],
            "helpful": helpful,
            "notes": notes,
        }
        self._append_log(self.feedback_log, record)

    def _append_log(self, filepath: str, record: dict) -> None:
        """
        Append a record to a JSONL log file.

        Args:
            filepath: Path to the log file
            record: Dictionary to log
        """
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            print(f"[WARNING] Could not write log: {e}")

    def get_summary(self) -> dict:
        """
        Return summary statistics from logs.

        Returns:
            Dictionary with counts of different events
        """
        summary = {
            "guardrail_blocks": self._count_events(self.guardrail_log),
            "retrieval_hits": self._count_events(self.retrieval_log, "retrieval_hit"),
            "retrieval_misses": self._count_events(self.retrieval_log, "retrieval_miss"),
            "answers_provided": self._count_events(self.retrieval_log, "answer_provided"),
            "feedback_helpful": self._count_events(self.feedback_log, "helpful"),
            "feedback_unhelpful": self._count_events(self.feedback_log, "not_helpful"),
        }
        return summary

    def _count_events(self, filepath: str, event_type: str = None) -> int:
        """Count events in a log file."""
        if not os.path.exists(filepath):
            return 0

        count = 0
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        record = json.loads(line)
                        if event_type is None or record.get("event") == event_type:
                            count += 1
                    except json.JSONDecodeError:
                        pass
        except Exception:
            pass

        return count


# Global logger instance
_logger: Optional[FAQLogger] = None


def get_logger() -> FAQLogger:
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        _logger = FAQLogger()
    return _logger


def init_logger(log_dir: str = ".") -> FAQLogger:
    """Initialize the global logger."""
    global _logger
    _logger = FAQLogger(log_dir)
    return _logger
