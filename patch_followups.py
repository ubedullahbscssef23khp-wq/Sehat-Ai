import sys
path = 'backend/app/conversation/followups.py'
content = open(path).read()

new_content = content.replace(
'''_FALLBACK_QUESTIONS: dict[str, str] = {
    "symptoms": (
        "Please describe the main symptoms: what do you feel, where, how severe "
        "(0-10), and for how long?"
    ),
    "demographics.age_group": (
        "What is the person's age group: infant, child, adolescent, adult, or older adult?"
    ),
    "demographics.pregnant": "Is there any possibility the person is pregnant?",
}

def _fallback_questions(fields: Sequence[str]) -> list[LocalizedText]:
    return [
        LocalizedText(en=_FALLBACK_QUESTIONS.get(field, f"Can you tell me more about: {field}?"))
        for field in fields
    ]''',
'''_FALLBACK_QUESTIONS: dict[str, LocalizedText] = {
    "symptoms": LocalizedText(
        en="Please describe the main symptoms: what do you feel, where, how severe (0-10), and for how long?",
        ur="براہ کرم اہم علامات بیان کریں: آپ کیا محسوس کرتے ہیں، کہاں، شدت (0-10)، اور کتنے عرصے سے؟",
        sd="مهرباني ڪري مکيه علامتون بيان ڪريو: توهان ڇا ٿا محسوس ڪريو، ڪٿي، شدت (0-10)، ۽ ڪيتري وقت کان؟"
    ),
    "demographics.age_group": LocalizedText(
        en="What is the person's age group: infant, child, adolescent, adult, or older adult?",
        ur="مریض کی عمر کا گروپ کیا ہے: نوزائیدہ، بچہ، نوعمر، بالغ، یا عمر رسیدہ؟",
        sd="مريض جي عمر جو گروپ ڇا آهي: نئون ڄاول، ٻار، نوجوان، بالغ، يا وڏي عمر جو؟"
    ),
    "demographics.pregnant": LocalizedText(
        en="Is there any possibility the person is pregnant?",
        ur="کیا اس بات کا کوئی امکان ہے کہ مریضہ حاملہ ہیں؟",
        sd="ڇا ان ڳالهه جو ڪو امڪان آهي ته مريضه حامله آهي؟"
    )
}

def _fallback_questions(fields: Sequence[str]) -> list[LocalizedText]:
    out = []
    for field in fields:
        if field in _FALLBACK_QUESTIONS:
            out.append(_FALLBACK_QUESTIONS[field])
        else:
            out.append(LocalizedText(
                en=f"Can you tell me more about: {field}?",
                ur=f"براہ کرم اس کے بارے میں مزید بتائیں: {field}",
                sd=f"مهرباني ڪري هن جي باري ۾ وڌيڪ ٻڌايو: {field}"
            ))
    return out''')

new_content = new_content.replace(
'''            return _fallback_questions(fields), True

        latency_ms = int((time.perf_counter() - started) * 1000)
        questions = _parse_questions(response.text, expected=len(fields))
        if questions is None:''',
'''            return _fallback_questions(fields), True

        latency_ms = int((time.perf_counter() - started) * 1000)
        questions = _parse_questions(response.text, expected=len(fields))
        if questions is None:'''
)

new_content = new_content.replace(
'''        return [LocalizedText(en=question) for question in questions], False''',
'''        out = []
        for i, q in enumerate(questions):
            field = fields[i] if i < len(fields) else ""
            fallback_en = _FALLBACK_QUESTIONS[field].en if field in _FALLBACK_QUESTIONS else f"Can you tell me more about: {field}?"
            if language == Language.UR:
                out.append(LocalizedText(en=fallback_en, ur=q))
            elif language == Language.SD:
                out.append(LocalizedText(en=fallback_en, sd=q))
            else:
                out.append(LocalizedText(en=q))
        return out, False'''
)
open(path, 'w').write(new_content)
print("patched backend/app/conversation/followups.py")
