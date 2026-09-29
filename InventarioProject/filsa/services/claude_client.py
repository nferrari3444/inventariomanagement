"""
Cliente reutilizable para la API de Claude (Anthropic).

Uso:

    from filsa.services.claude_client import ask_claude

    respuesta = ask_claude("Resumime este texto: ...")

La clave se lee de settings.ANTHROPIC_API_KEY (variable de entorno
ANTHROPIC_API_KEY en .env). Nunca hardcodear la clave en el código.
"""

import logging
from typing import Optional

import anthropic
from django.conf import settings

logger = logging.getLogger(__name__)

MODEL_DEFAULT = "claude-opus-5-5"

_client = None


def get_client() -> anthropic.Anthropic:
    """Devuelve un cliente Anthropic, creado una sola vez (singleton simple)."""
    global _client
    if _client is None:
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError(
                "ANTHROPIC_API_KEY no está configurada. Agregala al archivo .env."
            )
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


def ask_claude(prompt: str, system: Optional[str] = None, model: str = MODEL_DEFAULT) -> str:
    """
    Envía un prompt a Claude y devuelve el texto de la respuesta.

    Lanza las excepciones tipadas del SDK (anthropic.RateLimitError,
    anthropic.APIStatusError, anthropic.APIConnectionError, etc.) para que
    quien llame decida cómo manejarlas.
    """
    client = get_client()

    try:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.RateLimitError as exc:
        logger.warning("Claude API: rate limit alcanzado: %s", exc)
        raise
    except anthropic.APIConnectionError as exc:
        logger.error("Claude API: error de conexión: %s", exc)
        raise
    except anthropic.APIStatusError as exc:
        logger.error("Claude API: error %s: %s", exc.status_code, exc.message)
        raise

    return "".join(block.text for block in response.content if block.type == "text")
