import yaml
from pathlib import Path
from typing import Dict, Optional

class TranslationManager:
    def __init__(self, default_language: str = "en"):
        self.default_language = default_language
        self.translations: Dict[str, Dict[str, str]] = {}
        self.load_translations()
    
    def load_translations(self) -> None:
        """Load all translation files from the translations directory."""
        translations_dir = Path("translations")
        translations_dir.mkdir(exist_ok=True)
        
        # Create example translation files if they don't exist
        if not list(translations_dir.glob("*.yml")):
            self._create_example_translations()
        
        for file in translations_dir.glob("*.yml"):
            language = file.stem
            with open(file, "r", encoding="utf-8") as f:
                self.translations[language] = yaml.safe_load(f)
    
    def _create_example_translations(self) -> None:
        """Create example translation files for English, Spanish, and French."""
        example_translations = {
            "en": {
                "messages": {
                    "welcome": "Welcome to the server!",
                    "goodbye": "Goodbye!",
                    "help": "Here are the available commands:"
                },
                "errors": {
                    "not_found": "Command not found.",
                    "no_permission": "You don't have permission to use this command."
                }
            },
            "es": {
                "messages": {
                    "welcome": "¡Bienvenido al servidor!",
                    "goodbye": "¡Adiós!",
                    "help": "Aquí están los comandos disponibles:"
                },
                "errors": {
                    "not_found": "Comando no encontrado.",
                    "no_permission": "No tienes permiso para usar este comando."
                }
            },
            "fr": {
                "messages": {
                    "welcome": "Bienvenue sur le serveur !",
                    "goodbye": "Au revoir !",
                    "help": "Voici les commandes disponibles :"
                },
                "errors": {
                    "not_found": "Commande non trouvée.",
                    "no_permission": "Vous n'avez pas la permission d'utiliser cette commande."
                }
            }
        }
        
        translations_dir = Path("translations")
        for lang, translations in example_translations.items():
            with open(translations_dir / f"{lang}.yml", "w", encoding="utf-8") as f:
                yaml.dump(translations, f, allow_unicode=True, sort_keys=False)
    
    def get_text(self, key: str, language: str = None) -> str:
        """
        Get translated text for a given key and language.
        Supports nested keys using dot notation (e.g., 'messages.welcome')
        Falls back to default language if translation is missing.
        """
        language = language or self.default_language
        
        # Split the key into parts for nested access
        key_parts = key.split('.')
        
        # Try to get the translation in the requested language
        value = self._get_nested_value(self.translations.get(language, {}), key_parts)
        if value is not None:
            return value
        
        # Fall back to default language
        value = self._get_nested_value(self.translations.get(self.default_language, {}), key_parts)
        if value is not None:
            return value
        
        # Return the key itself if no translation is found
        return key
    
    def _get_nested_value(self, data: dict, keys: list) -> Optional[str]:
        """Helper method to get nested dictionary values."""
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
            else:
                return None
        return data if isinstance(data, str) else None
    
    def add_translation(self, language: str, key: str, text: str) -> None:
        """Add or update a translation. Supports nested keys using dot notation."""
        if language not in self.translations:
            self.translations[language] = {}
        
        # Split the key into parts for nested access
        current = self.translations[language]
        key_parts = key.split('.')
        
        # Navigate to the correct nested level
        for part in key_parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[key_parts[-1]] = text
        
        # Save to file
        translations_dir = Path("translations")
        with open(translations_dir / f"{language}.yml", "w", encoding="utf-8") as f:
            yaml.dump(self.translations[language], f, allow_unicode=True, sort_keys=False)