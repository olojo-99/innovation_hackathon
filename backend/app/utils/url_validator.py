import re
from typing import Tuple, Optional

def parse_challenge_url(url: str) -> Optional[Tuple[int, str, str, str]]:
    """
    Parse challenge URL in format: ERFT_stage{N}_p1-{val1}_p2-{val2}_p3-{val3}

    Returns:
        Tuple of (stage, p1, p2, p3) if valid, None otherwise
    """
    pattern = r"ERFT_stage(\d+)_p1-([^_]+)_p2-([^_]+)_p3-(.+)"
    match = re.match(pattern, url)

    if not match:
        return None

    stage, p1, p2, p3 = match.groups()
    return (int(stage), p1, p2, p3)

def count_correct_values(p1: str, p2: str, p3: str, challenge: dict) -> int:
    """
    Count how many submitted values match the correct answers.
    Returns count without revealing which ones are correct.
    """
    correct_count = sum([
        p1 == challenge["correct_p1"],
        p2 == challenge["correct_p2"],
        p3 == challenge["correct_p3"]
    ])
    return correct_count
