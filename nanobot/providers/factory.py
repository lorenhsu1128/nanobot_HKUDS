"""
Factory for creating LLM providers from configuration.
"""
from typing import Optional

from nanobot.config.schema import Config
from nanobot.providers.base import LLMProvider
from nanobot.providers.registry import find_by_name


class ProviderConfigurationError(Exception):
    """Raised when provider configuration is invalid."""
    pass


class ProviderFactory:
    """Factory class for creating LLM providers."""

    @staticmethod
    def create(config: Config) -> LLMProvider:
        """
        Create an LLM provider instance based on the configuration.

        Args:
            config: The application configuration.

        Returns:
            An instance of LLMProvider.

        Raises:
            ProviderConfigurationError: If the provider cannot be configured (e.g. missing API key).
        """
        from nanobot.providers.litellm_provider import LiteLLMProvider
        from nanobot.providers.openai_codex_provider import OpenAICodexProvider

        model = config.agents.defaults.model
        provider_name = config.get_provider_name(model)
        p = config.get_provider(model)

        # OpenAI Codex (OAuth): don't route via LiteLLM; use the dedicated implementation.
        if provider_name == "openai_codex" or model.startswith("openai-codex/"):
            return OpenAICodexProvider(default_model=model)

        spec = find_by_name(provider_name)
        
        # Validation checks
        has_key = p and p.api_key
        is_bedrock = model.startswith("bedrock/")
        is_oauth = spec and spec.is_oauth

        if not is_bedrock and not has_key and not is_oauth:
             raise ProviderConfigurationError(
                 "No API key configured.\n"
                 "Set one in ~/.nanobot/config.json under providers section."
             )

        return LiteLLMProvider(
            api_key=p.api_key if p else None,
            api_base=config.get_api_base(model),
            default_model=model,
            extra_headers=p.extra_headers if p else None,
            provider_name=provider_name,
        )
