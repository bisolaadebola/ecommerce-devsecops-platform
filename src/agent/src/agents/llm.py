#!/usr/bin/python

# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

import os

from langchain_anthropic import ChatAnthropic
from src.agents.patch_vcr import VCR


class ChatLLM(ChatAnthropic):
    def __init__(self, **kwargs):
        model_name = os.getenv("LLM_MODEL", "claude-opus-5-5")
        use_vcr = os.getenv("USE_VCR", "True").lower() == "true"
        cassette_name = ""
        if use_vcr:
            cassette_name = f"{model_name.replace('/', '_')}_cassette.yaml"
        kwargs.setdefault("model", model_name)
        kwargs.setdefault("max_tokens", 16000)
        # Defaults to https://api.anthropic.com when unset
        kwargs.setdefault("base_url", os.getenv("ANTHROPIC_BASE_URL"))

        api_key = os.getenv("API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            api_key = "sk-dummy"
        kwargs.setdefault("api_key", api_key)
        # Only needed when the API key is not scoped to a workspace
        workspace_id = os.getenv("ANTHROPIC_WORKSPACE_ID")
        if workspace_id:
            kwargs.setdefault("default_headers", {"anthropic-workspace-id": workspace_id})

        super().__init__(**kwargs)

        object.__setattr__(self, "_use_vcr", use_vcr)
        object.__setattr__(self, "_cassette_name", cassette_name)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        if getattr(self, "_use_vcr", False):
            with VCR.use_cassette(self._cassette_name):
                return super()._generate(messages, stop, run_manager, **kwargs)
        return super()._generate(messages, stop, run_manager, **kwargs)

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        if getattr(self, "_use_vcr", False):
            with VCR.use_cassette(self._cassette_name):
                return await super()._agenerate(messages, stop, run_manager, **kwargs)
        return await super()._agenerate(messages, stop, run_manager, **kwargs)
