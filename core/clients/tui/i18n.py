"""
UNIBOS TUI Internationalization (i18n) System
Simple translation system for multi-language support
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any

# Config directory for persistent settings
CONFIG_DIR = Path.home() / '.config' / 'unibos'
LANGUAGE_PREF_FILE = CONFIG_DIR / 'language.json'


class TranslationManager:
    """
    Manages translations for the TUI

    This provides a simple gettext-like interface for translating
    UI strings across the UNIBOS TUI system.
    """

    def __init__(self, default_language: str = 'tr'):
        """
        Initialize translation manager

        Args:
            default_language: Default language code (tr, en, etc.)
        """
        self.translations: Dict[str, Dict[str, str]] = {}
        self.translations_dir = Path(__file__).parent / 'translations'

        # Load all available translations
        self.load_translations()

        # Load saved language preference, or use default
        saved_lang = self._load_language_preference()
        self.current_language = saved_lang if saved_lang else default_language

    def _load_language_preference(self) -> Optional[str]:
        """Load saved language preference from config file"""
        try:
            if LANGUAGE_PREF_FILE.exists():
                with open(LANGUAGE_PREF_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('language')
        except (json.JSONDecodeError, IOError, OSError):
            pass
        return None

    def _save_language_preference(self, lang_code: str) -> bool:
        """Save language preference to config file"""
        try:
            # Create config directory if it doesn't exist
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            with open(LANGUAGE_PREF_FILE, 'w', encoding='utf-8') as f:
                json.dump({'language': lang_code}, f, indent=2)
            return True
        except (IOError, OSError):
            return False

    def load_translations(self):
        """Load all translation files from translations directory"""
        # Create translations directory if it doesn't exist
        self.translations_dir.mkdir(exist_ok=True)

        # Load each translation file
        if self.translations_dir.exists():
            for lang_file in self.translations_dir.glob('*.json'):
                lang_code = lang_file.stem
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                except (json.JSONDecodeError, IOError):
                    # Skip invalid files
                    pass

    def set_language(self, language_code: str, save: bool = True) -> bool:
        """
        Set current language

        Args:
            language_code: Language code (tr, en, de, etc.)
            save: Whether to save preference to disk (default True)

        Returns:
            True if language was set successfully, False otherwise
        """
        # Normalize language code
        language_code = language_code.lower()

        # Check if translations exist for this language
        if language_code in self.translations:
            self.current_language = language_code
            if save:
                self._save_language_preference(language_code)
            return True

        # Default to English or Turkish if not found
        if language_code not in ['en', 'tr']:
            self.current_language = 'en'
            if save:
                self._save_language_preference('en')
            return False

        self.current_language = language_code
        if save:
            self._save_language_preference(language_code)
        return True

    def get_language(self) -> str:
        """Get current language code"""
        return self.current_language

    def translate(self, key: str, **kwargs) -> str:
        """
        Translate a key to current language

        Args:
            key: Translation key
            **kwargs: Format arguments for string formatting

        Returns:
            Translated string (or key if translation not found)
        """
        # Get translation for current language
        lang_dict = self.translations.get(self.current_language, {})
        translated = lang_dict.get(key, key)

        # Apply formatting if provided
        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except (KeyError, ValueError):
                # If formatting fails, return unformatted
                pass

        return translated

    def t(self, key: str, **kwargs) -> str:
        """
        Short alias for translate()

        Args:
            key: Translation key
            **kwargs: Format arguments

        Returns:
            Translated string
        """
        return self.translate(key, **kwargs)

    def get_language_display_name(self, lang_code: str) -> str:
        """
        Get display name for a language

        Args:
            lang_code: Language code

        Returns:
            Display name (e.g., "Türkçe" for "tr")
        """
        display_names = {
            'tr': 'türkçe',
            'en': 'english',
            'de': 'deutsch',
            'fr': 'français',
            'es': 'español',
            'it': 'italiano',
            'pt': 'português',
            'ru': 'русский',
            'ar': 'العربية',
            'zh': '中文',
        }
        return display_names.get(lang_code, lang_code)

    def get_language_flag(self, lang_code: str) -> str:
        """
        Get flag emoji for a language

        Args:
            lang_code: Language code

        Returns:
            Flag emoji
        """
        flags = {
            'tr': '🇹🇷',
            'en': '🇬🇧',
            'de': '🇩🇪',
            'fr': '🇫🇷',
            'es': '🇪🇸',
            'it': '🇮🇹',
            'pt': '🇵🇹',
            'ru': '🇷🇺',
            'ar': '🇸🇦',
            'zh': '🇨🇳',
        }
        return flags.get(lang_code, '🌐')

    def get_available_languages(self) -> list:
        """
        Get list of available languages

        Returns:
            List of tuples: (code, name, flag)
        """
        # Return all supported languages (even if translations don't exist yet)
        languages = [
            ('tr', 'türkçe', '🇹🇷'),
            ('en', 'english', '🇬🇧'),
            ('de', 'deutsch', '🇩🇪'),
            ('fr', 'français', '🇫🇷'),
            ('es', 'español', '🇪🇸'),
            ('it', 'italiano', '🇮🇹'),
            ('pt', 'português', '🇵🇹'),
            ('ru', 'русский', '🇷🇺'),
            ('ar', 'العربية', '🇸🇦'),
            ('zh', '中文', '🇨🇳'),
        ]
        return languages


# Global translation manager instance
_translation_manager: Optional[TranslationManager] = None


def get_translation_manager() -> TranslationManager:
    """
    Get global translation manager instance

    Returns:
        TranslationManager instance
    """
    global _translation_manager
    if _translation_manager is None:
        _translation_manager = TranslationManager()
    return _translation_manager


def t(key: str, **kwargs) -> str:
    """
    Global translation function

    Args:
        key: Translation key
        **kwargs: Format arguments

    Returns:
        Translated string
    """
    return get_translation_manager().translate(key, **kwargs)


def set_language(lang_code: str) -> bool:
    """
    Set global language

    Args:
        lang_code: Language code

    Returns:
        True if successful
    """
    return get_translation_manager().set_language(lang_code)


def get_language() -> str:
    """
    Get current language

    Returns:
        Current language code
    """
    return get_translation_manager().get_language()
