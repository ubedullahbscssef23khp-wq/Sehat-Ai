from pathlib import Path

content = Path('backend/tests/test_headache_vertical_slice.py').read_text()

import re

new_assertions = """
        assert len(evidence) > 0
        assert "source" in evidence[0]
        assert "WHO" in evidence[0]["source"]
        assert "date_reviewed" in evidence[0]
"""

content = re.sub(
    r'assert len\(evidence\) > 0.*?pass',
    new_assertions.strip(),
    content,
    flags=re.DOTALL
)

Path('backend/tests/test_headache_vertical_slice.py').write_text(content)
