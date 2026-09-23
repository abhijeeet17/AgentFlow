import json
import httpx
from typing import Optional, Type
from pydantic import BaseModel
from app.llm.base import BaseLLMProvider
from app.config import settings

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip('/')
        self.model = model or settings.OLLAMA_MODEL

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        system_prompt: Optional[str] = None
    ) -> BaseModel:
        schema_json = response_model.model_json_schema()
        json_prompt = (
            f"{prompt}\n\n"
            f"Output MUST be valid JSON adhering strictly to this JSON schema:\n"
            f"{json.dumps(schema_json, indent=2)}\n"
            f"Do not include any explanation outside the JSON."
        )
        
        sys_p = system_prompt or "You are a precise JSON generating AI assistant."
        raw_response = await self.generate_text(json_prompt, sys_p)
        
        # Parse JSON from response
        cleaned = raw_response.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
        json_data = json.loads(cleaned)
        return response_model.model_validate(json_data)
