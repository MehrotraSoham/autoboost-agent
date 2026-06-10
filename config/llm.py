"""
LLM provider switcher.

Set LLM_PROVIDER in .env to choose which model powers the agent:
  LLM_PROVIDER=gemini     → Google Gemini 2.5 Flash (free tier)
  LLM_PROVIDER=anthropic  → Claude Haiku (requires paid API key)

Both providers are fully supported. Switching is a one-line .env change.
"""
from langchain_core.language_models import BaseChatModel


def get_llm(max_tokens: int = 1024) -> BaseChatModel:
    from config.brand_config import settings

    if settings.llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-haiku-4-5-20251001",
            api_key=settings.anthropic_api_key,
            max_tokens=max_tokens,
        )

    # Default: Gemini
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.google_api_key,
        max_output_tokens=max_tokens,
    )
