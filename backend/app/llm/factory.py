import logging
from app.llm.base import BaseLLMProvider
from app.llm.mock_provider import MockLLMProvider
from app.config import settings

logger = logging.getLogger(__name__)

def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    provider = (provider_name or settings.LLM_PROVIDER).lower()
    
    if provider == "openai":
        try:
            from app.llm.openai_provider import OpenAIProvider
            return OpenAIProvider()
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAIProvider ({e}). Falling back to MockLLMProvider.")
            return MockLLMProvider()
    elif provider == "ollama":
        try:
            from app.llm.ollama_provider import OllamaProvider
            return OllamaProvider()
        except Exception as e:
            logger.warning(f"Failed to initialize OllamaProvider ({e}). Falling back to MockLLMProvider.")
            return MockLLMProvider()
    else:
        return MockLLMProvider()
