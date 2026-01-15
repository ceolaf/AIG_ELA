# AIG_prompts.py
# Builds the tier prompts for each LLM based on the standard, files, and passage.

from typing import List, Tuple
from AIG_config import RESULTS_SUFFIX


def BuildTiers(standard_code: str, passage: str) -> List[Tuple[str, str, str]]:
    """
    Build all prompt tiers for a given standard + passage.

    Returns:
        A list of tuples in the form:
            (tier_code, prompt_text, output_filename)
    """

    # --- Load component files ---

    with open("Standard.txt", encoding="utf-8") as f:
        standard = f.read().strip()

    prompt_part1 = (
        "You are an expert content development professional writing high quality "
        "items for large scale assessments for 8th grade based on the following "
        "passage. Please write a unique multiple choice items (if you can) aligned "
        f"to {standard} using the following literary passage."
    )

    with open("Yes50.txt", encoding="utf-8") as f:
        yes50 = "That standard means, " + f.read()

    with open("Yes100.txt", encoding="utf-8") as f:
        yes100 = "That standard means, " + f.read()

    with open("No50.txt", encoding="utf-8") as f:
        no50 = "However, " + f.read()

    with open("No100.txt", encoding="utf-8") as f:
        no100 = "However, " + f.read()

    with open("Misconceptions.txt", encoding="utf-8") as f:
        misconceptions = (
            "\n\nDistractors may be based upon the following misconceptions or "
            "mistakes-- or upon other errors with the *targeted* cognition.\n"
            + f.read()
        )

    prompt_part2 = (
        "\n\nBasic Instructions:\n\n"
        "· The key (i.e, the correct answer option) should be marked with an “*”.\n\n"
        "· The item should have three distractors.\n\n"
        "· Please include rationales for each answer option that lay out the steps or "
        "reasoning that would lead to each response.\n\n"
        "· If you revise the item, please make sure to include the full final "
        "version at the end.\n\n"
    )

    with open("LBIDAT.md", encoding="utf-8") as f:
        LBIDAT = (
            "**** Your goal is for each item to score well on the LBIDAT criteria, "
            "whose complete text is included below. ***\n\n" + f.read()
        )

    # --- Build all the prompts ---

    prompt_2a = prompt_part1 + prompt_part2 + passage
    prompt_2b = prompt_part1 + prompt_part2 + LBIDAT + passage

    prompt_3a = prompt_part1 + yes50 + prompt_part2 + passage
    prompt_3b = prompt_part1 + yes50 + prompt_part2 + LBIDAT + passage

    prompt_4a = prompt_part1 + yes100 + prompt_part2 + passage
    prompt_4b = prompt_part1 + yes100 + prompt_part2 + LBIDAT + passage

    prompt_5a = prompt_part1 + yes100 + no50 + prompt_part2 + passage
    prompt_5b = prompt_part1 + yes100 + no50 + prompt_part2 + LBIDAT + passage

    prompt_6a = prompt_part1 + yes100 + no100 + prompt_part2 + passage
    prompt_6b = prompt_part1 + yes100 + no100 + prompt_part2 + LBIDAT + passage

    prompt_7a = prompt_part1 + yes100 + no100 + prompt_part2 + misconceptions + passage
    prompt_7b = (
        prompt_part1 + yes100 + no100 + prompt_part2 + misconceptions + LBIDAT + passage
    )

    # --- Build output filenames using config RESULTS_SUFFIX ---

    base_dir = f"{standard_code}{RESULTS_SUFFIX}"

    tiers: List[Tuple[str, str, str]] = [
        ("2a", prompt_2a, f"{base_dir}/{standard_code} Tier 2a Item Output.txt"),
        ("2b", prompt_2b, f"{base_dir}/{standard_code} Tier 2b Item Output.txt"),
        ("3a", prompt_3a, f"{base_dir}/{standard_code} Tier 3a Item Output.txt"),
        ("3b", prompt_3b, f"{base_dir}/{standard_code} Tier 3b Item Output.txt"),
        ("4a", prompt_4a, f"{base_dir}/{standard_code} Tier 4a Item Output.txt"),
        ("4b", prompt_4b, f"{base_dir}/{standard_code} Tier 4b Item Output.txt"),
        ("5a", prompt_5a, f"{base_dir}/{standard_code} Tier 5a Item Output.txt"),
        ("5b", prompt_5b, f"{base_dir}/{standard_code} Tier 5b Item Output.txt"),
        ("6a", prompt_6a, f"{base_dir}/{standard_code} Tier 6a Item Output.txt"),
        ("6b", prompt_6b, f"{base_dir}/{standard_code} Tier 6b Item Output.txt"),
        ("7a", prompt_7a, f"{base_dir}/{standard_code} Tier 7a Item Output.txt"),
        ("7b", prompt_7b, f"{base_dir}/{standard_code} Tier 7b Item Output.txt"),
    ]

    return tiers
