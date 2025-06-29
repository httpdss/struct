import os
import logging
from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()

class ModelWrapper:
  """
  Wraps model logic using pydantic-ai Agent, allowing use of multiple LLM providers.
  """
  def __init__(self, logger=None):
    self.logger = logger or logging.getLogger(__name__)
    self.model_name = os.getenv("AI_MODEL") or "openai:gpt-4.1"
    self.agent = Agent(model=self.model_name)
    self.logger.debug(f"Configured Agent with model: {self.model_name}")

  def generate_content(self, system_prompt, user_prompt, dry_run=False):
    if not self.agent:
      self.logger.warning("No agent configured. Skipping content generation.")
      return "No agent configured. Skipping content generation."
    if dry_run:
      self.logger.info("[DRY RUN] Would generate content using AI agent.")
      return "[DRY RUN] Generating content using AI agent"
    prompt = f"{user_prompt}"
    try:
      self.agent.system_prompt = system_prompt
      result = self.agent.run_sync(prompt)
      return result.output
    except Exception as e:
      self.logger.error(f"AI agent generation failed: {e}")
      return f"AI agent generation failed: {e}"
