from arabic_reshaper import reshape
from bidi.algorithm import get_display

def fa(text: str) -> str:
    """تبدیل متن فارسی به شکل قابل نمایش درست در Kivy"""
    if not text:
        return text
    reshaped = reshape(text)
    return get_display(reshaped)