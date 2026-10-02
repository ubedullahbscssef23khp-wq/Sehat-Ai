from pathlib import Path

content = Path('backend/tests/test_emergency_vertical_slice.py').read_text()

replacement = """
def test_pending_and_rejected_patterns_do_not_activate(tmp_path: Path):
    pend = make_stroke_pattern("P1", "test")
    pend.review_status = ReviewStatus.PENDING_DOMAIN_REVIEW
    
    rej = make_stroke_pattern("R1", "test")
    rej.review_status = ReviewStatus.REJECTED
    
    from app.safety.loader import load_patterns_dir
    import yaml
    
    data = {
        "patterns": [
            pend.model_dump(mode="json"),
            rej.model_dump(mode="json")
        ]
    }
    test_file = tmp_path / "test.yaml"
    test_file.write_text(yaml.dump(data))
    
    loaded = load_patterns_dir(tmp_path)
    assert len(loaded) == 0
"""

import re
content = re.sub(r'def test_pending_and_rejected_patterns_do_not_activate\(\):.*?(?=def test_unknown_red_flag_signal_fails_closed\(\):)', replacement + '\n', content, flags=re.DOTALL)

Path('backend/tests/test_emergency_vertical_slice.py').write_text(content)
