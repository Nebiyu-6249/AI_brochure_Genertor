import os
from app.config import require_openai_key, settings


class OpenAIService:
    def __init__(self):
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "openai package is required. Install dependencies: pip install -r requirements.txt"
            ) from e

        self.client = OpenAI(api_key=require_openai_key())

    @property
    def chat_model(self) -> str:
        return os.getenv("OPENAI_CHAT_MODEL", settings.openai_chat_model)

    def chat_json(self, system: str, user: str) -> dict:
        """Ask the model to return a JSON object (with fallback)."""
        import json, re
        try:
            resp = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            content = resp.choices[0].message.content or "{}"
            return json.loads(content)
        except Exception:
            resp = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user + "\n\nReturn ONLY JSON."}],
                temperature=0.2,
            )
            raw = resp.choices[0].message.content or "{}"
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            return json.loads(m.group(0) if m else "{}")

    def chat_markdown(self, system: str, user: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.chat_model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.4,
        )
        return resp.choices[0].message.content or ""
