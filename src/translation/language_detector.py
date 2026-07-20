from langdetect import detect

def detect_language(text):

    try:

        text = text.strip()

        if not text:
            return "en"

        language = detect(text)

        # Support Hindi explicitly
        if language == "hi":
            return "hi"

        # Everything else becomes English
        return "en"

    except Exception:
        return "en"