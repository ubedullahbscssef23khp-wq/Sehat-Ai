import json
import yaml
import glob
from pathlib import Path

knowledge_files = glob.glob("app/knowledge/clinical/**/*.md", recursive=True)
rules_files = glob.glob("app/safety/rules/**/*.yaml", recursive=True)

patterns = 0
for f in rules_files:
    try:
        with open(f, 'r') as fp:
            data = yaml.safe_load(fp)
            if data and 'patterns' in data:
                patterns += len(data['patterns'])
    except Exception:
        pass

print(f"Production Emergency Patterns: {patterns}")
print(f"Production Knowledge Entries: {len(knowledge_files)}")
