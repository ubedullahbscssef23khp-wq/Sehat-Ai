with open("backend/scripts/prepare_befast_review.py", "r") as f:
    lines = f.readlines()
with open("backend/scripts/prepare_befast_review.py", "w") as f:
    for line in lines:
        if "Source URL:**" in line and "review_doc" in line:
            f.write("    review_doc.append(f\"- **Source URL:** {c['source_url']}\")\n")
            f.write("    review_doc.append(f\"- **Publication Date:** {c['publication_date']}\")\n")
        else:
            f.write(line)
