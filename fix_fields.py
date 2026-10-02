with open("backend/scripts/prepare_befast_review.py", "r") as f:
    content = f.read()

old_block = """    review_doc.append(f"- **Review Status:** PENDING_DOMAIN_REVIEW")
    review_doc.append(f"- **Reviewer Fields:** Awaiting `reviewed_by` and `reviewed_at`\\n")"""

new_block = """    review_doc.append(f"- **Review Status:** PENDING_DOMAIN_REVIEW")
    review_doc.append(f"- **Required reviewer qualification:** QUALIFIED_CLINICAL_REVIEWER")
    review_doc.append(f"- **Clinical decision field:** ")
    review_doc.append(f"- **Reviewer identity field:** ")
    review_doc.append(f"- **Review timestamp field:** ")
    review_doc.append(f"- **Clinical approval reference field:** ")
    review_doc.append(f"- **Reviewer comments field:** \\n")"""

content = content.replace(old_block, new_block)

with open("backend/scripts/prepare_befast_review.py", "w") as f:
    f.write(content)
