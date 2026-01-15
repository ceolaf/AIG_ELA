# AIG_output.py
# Centralized helper for writing LLM results to both file and screen.

from AIG_config import FIRST_ITEM_TEMP, NEXT_ITEM_TEMP


def PrintToFileAndScreen(
    LLM: str,
    tier_code: str,
    index: int,
    response: str,
    file_name: str,
    passage_name: str,
    elapsed: float,
    input_tokens: int,
    output_tokens: int,
) -> None:
    """
    Write a single generated item to the results file and echo it to stdout.

    Parameters
    ----------
    LLM : str
        Name of the LLM ("GPT", "Gemini", "Claude", "Copilot", etc.).
    tier_code : str
        Tier label (e.g., "2a", "3b").
    index : int
        Item index (1-based) within this tier/LLM run.
    response : str
        Raw text returned by the LLM.
    file_name : str
        Path to the output file for this tier.
    passage_name : str
        File name of the passage used (for reference in the log).
    elapsed : float
        Elapsed time in seconds for this call.
    input_tokens : int
        Number of input tokens (0 for models that don't report).
    output_tokens : int
        Number of output tokens (0 for models that don't report).
    """

    # Human-readable temperature label (for non-Copilot runs)
    if LLM == "Copilot":
        temperature_suffix = ""
    else:
        temp = FIRST_ITEM_TEMP if index == 1 else NEXT_ITEM_TEMP
        temperature_suffix = f" (temp={temp})"

    total_tokens = input_tokens + output_tokens

    # ---- Write to file ----
    with open(file_name, "a", encoding="utf-8") as f:
        f.write("\n\n\n================= NEW ITEM =================")
        f.write(f"\nPassage: {passage_name}")
        f.write(
            f"\nTier {tier_code} ({LLM}) #{index}{temperature_suffix}. "
            f"({elapsed:.2f} secs). "
            f"({input_tokens} + {output_tokens} = {total_tokens} total tokens)\n\n"
        )
        f.write(response)

    # ---- Echo to screen ----
    print("\n\n================= NEW ITEM =================")
    print(
        f"\nTier {tier_code} ({LLM}) #{index}{temperature_suffix}. "
        f"({elapsed:.2f} secs)\n"
    )
    print(response)
    print(f"\n\nTier {tier_code} #{index} complete, saved to {file_name}\n")
