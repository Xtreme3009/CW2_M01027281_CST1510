import os
import requests
from typing import List, Dict, Union


OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


class AIServiceError(Exception):
    """Raised for any errors when calling the AI service."""
    pass


def _get_api_key() -> str:
    """Read API key from env and raise an error if missing."""
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise AIServiceError("OPENAI_API_KEY not found in environment")
    return key


def chat_completion(
    prompt: Union[str, List[Dict[str, str]]],
    model: str = "gpt-3.5-turbo",
    max_tokens: int = 500,
    temperature: float = 0.2,
) -> str:
    """Send a chat-style completion request to the OpenAI API.

    prompt may be a single user string or a list of message dicts
    in the form [{"role": "user", "content": "..."}, ...].
    Returns the assistant reply as a string. Network and API errors
    are raised as AIServiceError.
    """
    api_key = _get_api_key()

    if isinstance(prompt, str):
        messages = [{"role": "user", "content": prompt}]
    else:
        messages = prompt

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(OPENAI_API_URL, json=payload, headers=headers, timeout=30)
    except requests.RequestException as e:
        raise AIServiceError(f"Network error when calling OpenAI: {e}")

    if resp.status_code != 200:
        # try to include any API error message
        try:
            body = resp.json()
            msg = body.get("error", {}).get("message") or str(body)
        except Exception:
            msg = resp.text
        raise AIServiceError(f"OpenAI API error {resp.status_code}: {msg}")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise AIServiceError(f"Unexpected response format from OpenAI: {e}")
