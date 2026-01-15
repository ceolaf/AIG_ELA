"""
RTD Central Tenet (or Mantra):
Valid items elicit evidence of the targeted cognition for the range of typical test takers.

This script exists to experiment with AIG *only* insofar as it helps us generate, 
refine, or study items that remain valid by that standard. Efficiency gains that reduce 
item validity are out of scope and not acceptable.
"""

# AIG_main.py
# Orchestrates the overall workflow:
# - pick standard & passage
# - check files
# - build prompts/tiers
# - run selected LLMs

import os

from AIG_ui import (
    SelectStandard,
    SelectPassage,
    CheckRequiredFiles,
    AskLLMs,
    AskItemsPerTier,
)

from AIG_prompts import BuildTiers
from AIG_runners import RunGPT, RunGemini, RunClaude, RunCopilot
from AIG_config import RESULTS_SUFFIX


def main() -> None:

    # 1. Pick the CCSS standard directory
    standard_code = SelectStandard()
    if not standard_code:
        return

    # 2. Pick the passage inside Passages/ or fallback directories
    passage_name, passage_text = SelectPassage()
    if passage_text is None:
        return

    # 3. Move into that standard's directory
    os.chdir(standard_code)

    # 4. Confirm required files exist
    if not CheckRequiredFiles():
        return

    # 5. Create the results directory
    results_dir = f"{standard_code}{RESULTS_SUFFIX}"
    os.makedirs(results_dir, exist_ok=True)

    # 6. Build all prompt tiers
    tiers = BuildTiers(standard_code, passage_text)

    # 7. Prompt the user for which LLMs to run
    LLMs_selected = AskLLMs()

    # 8. How many items per tier?
    item_per_tier = AskItemsPerTier()

    # 9. Run selected LLMs
    if "GPT" in LLMs_selected:
        RunGPT(tiers, item_per_tier, passage_name)

    if "Gemini" in LLMs_selected:
        RunGemini(tiers, item_per_tier, passage_name)

    if "Claude" in LLMs_selected:
        RunClaude(tiers, item_per_tier, passage_name)

    if "Copilot" in LLMs_selected:
        RunCopilot(tiers, item_per_tier, passage_name)


if __name__ == "__main__":
    main()
