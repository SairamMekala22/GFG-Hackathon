import json
import os

import requests
from requests import HTTPError


class GeminiService:
    @property
    def api_key(self):
        return os.getenv("GEMINI_API_KEY")

    @property
    def model(self):
        return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    @property
    def base_url(self):
        return f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate_text(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("Gemini API key is not configured.")

        response = requests.post(
            self.base_url,
            params={"key": self.api_key},
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=40,
        )

        try:
            response.raise_for_status()
        except HTTPError as error:
            detail = self._extract_error_detail(response)
            raise RuntimeError(
                f"Gemini request failed ({response.status_code}): {detail}"
            ) from error

        payload = response.json()
        candidates = payload.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini returned no candidates.")

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts).strip()
        if not text:
            raise RuntimeError("Gemini returned empty content.")
        return text

    def generate_json(self, prompt: str) -> dict:
        text = self.generate_text(prompt)
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(text)

    @staticmethod
    def _extract_error_detail(response) -> str:
        try:
            payload = response.json()
        except ValueError:
            payload = None

        if isinstance(payload, dict):
            error = payload.get("error", {})
            message = error.get("message")
            status = error.get("status")
            if message and status:
                return f"{status}: {message}"
            if message:
                return message

        return "Unknown Gemini API error."


gemini_service = GeminiService()
