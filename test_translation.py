from src.translation.language_detector import (
    detect_language
)

from src.translation.translator import (
    translate_to_english,
    translate_from_english
)

question = "न्यूनतम मजदूरी अधिनियम क्या है?"

lang = detect_language(question)

print("Language:", lang)

english = translate_to_english(question)

print("\nEnglish:")

print(english)

hindi = translate_from_english(
    english,
    "hi"
)

print("\nBack To Hindi:")

print(hindi)