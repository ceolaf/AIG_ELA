import os
from openai import OpenAI

client = OpenAI()


def AskLLMs():
    while True:
        print("\n" + "═" * 45)
        print("   Select an LLM for Item Generation")
        print("═" * 45)
        print("  1) Anthropic's Claude")
        print("  2) Google's Gemini")
        print("  3) Microsoft's Copilot")
        print("  4) OpenAI's GPT")
        print("  5) All of the above")
        print("═" * 45)

        UserChoice = input("Enter your choice (1–5): ").strip()

        match UserChoice:
            case "1":
                return ["Claude"]
            case "2":
                return ["Gemini"]
            case "3":
                return ["Copilot"]
            case "4":
                return ["GPT"]
            case "5":
                return ["Claude", "Gemini", "Copilot", "GPT"]
            case _:
                print("\nInvalid choice. Please enter a number from 1 to 5.")


def AskItemsPerTier():
    while True:
        Answer = input("How many items per tier do you want? (1 or more): ").strip()
        if not Answer.isdigit():
            print("Please enter a whole number like 1, 2, 3...")
            continue

        Count = int(Answer)
        if Count < 1:
            print("Please enter a number 1 or greater.")
            continue

        return Count


def BuildTiers():
    # Read the prompt components
    with open("Standard Code.md") as f:
        StandardCode = f.read().strip()

    with open("Standard.txt") as f:
        Standard = f.read().strip()

    PromptPart1 = (
        "You are an expert content development professional writing high quality "
        "items for large scale assessments for 8th grade based on the following "
        "passage. Please write a unique multiple choice items (if you can) aligned "
        f"to {Standard} using the following literary passage."
    )

    with open("Yes50.txt") as f:
        Yes50 = "That standard means, " + f.read()

    with open("Yes100.txt") as f:
        Yes100 = "That standard means, " + f.read()

    with open("No50.txt") as f:
        No50 = "However, " + f.read()

    with open("No100.txt") as f:
        No100 = "However, " + f.read()

    with open("Misconceptions.txt") as f:
        Misconceptions = (
            "\n\nDistractors may be based upon the following misconceptions or "
            "mistakes-- or upon other errors with the *targeted* cognition.\n"
            + f.read()
        )

    PromptPart2 = (
        "\n\nBasic Instructions:\n\n"
        "· The key (i.e, the correct answer option] should be marked with an “*”.\n\n"
        "· The item should have three distractors.\n\n"
        "· Please include rationales for each answer option that lay out the steps or "
        "reasoning that would lead to each response.\n\n"
        "· If you revise the item, please make sure to include the full final "
        "version at the end.\n\n"
    )

    with open("LBIDAT.md") as f:
        LBIDAT = (
            "**** Your goal is for each item to score well on the LBIDAT criteria, "
            "whose complete text is included below. ***\n\n"
            + f.read()
        )

    with open("Passage.txt") as f:
        Passage = (
            "================== Passage Text =================\n\n"
            + f.read()
            + "\n\n"
        )

    # Build each prompt
    Prompt2a = PromptPart1 + PromptPart2 + Passage
    Prompt2b = PromptPart1 + PromptPart2 + LBIDAT + Passage
    Prompt3a = PromptPart1 + Yes50 + PromptPart2 + Passage
    Prompt3b = PromptPart1 + Yes50 + PromptPart2 + LBIDAT + Passage
    Prompt4a = PromptPart1 + Yes100 + PromptPart2 + Passage
    Prompt4b = PromptPart1 + Yes100 + PromptPart2 + LBIDAT + Passage
    Prompt5a = PromptPart1 + Yes100 + No50 + PromptPart2 + Passage
    Prompt5b = PromptPart1 + Yes100 + No50 + PromptPart2 + LBIDAT + Passage
    Prompt6a = PromptPart1 + Yes100 + No100 + PromptPart2 + Passage
    Prompt6b = PromptPart1 + Yes100 + No100 + PromptPart2 + LBIDAT + Passage
    Prompt7a = PromptPart1 + Yes100 + No100 + PromptPart2 + Misconceptions + Passage
    Prompt7b = PromptPart1 + Yes100 + No100 + PromptPart2 + Misconceptions + LBIDAT + Passage

    # Create the Tiers list (tier code, prompt text, filename)
    Tiers = [
        ("2a", Prompt2a, f"Results/{StandardCode} Tier 2a Item Output.txt"),
        ("2b", Prompt2b, f"Results/{StandardCode} Tier 2b Item Output.txt"),
        ("3a", Prompt3a, f"Results/{StandardCode} Tier 3a Item Output.txt"),
        ("3b", Prompt3b, f"Results/{StandardCode} Tier 3b Item Output.txt"),
        ("4a", Prompt4a, f"Results/{StandardCode} Tier 4a Item Output.txt"),
        ("4b", Prompt4b, f"Results/{StandardCode} Tier 4b Item Output.txt"),
        ("5a", Prompt5a, f"Results/{StandardCode} Tier 5a Item Output.txt"),
        ("5b", Prompt5b, f"Results/{StandardCode} Tier 5b Item Output.txt"),
        ("6a", Prompt6a, f"Results/{StandardCode} Tier 6a Item Output.txt"),
        ("6b", Prompt6b, f"Results/{StandardCode} Tier 6b Item Output.txt"),
        ("7a", Prompt7a, f"Results/{StandardCode} Tier 7a Item Output.txt"),
        ("7b", Prompt7b, f"Results/{StandardCode} Tier 7b Item Output.txt"),
    ]

    return Tiers


def RunGPT(Tiers):
    for TierCode, PromptText, FileName in Tiers:
        # First item
        Response1 = client.responses.create(
            model="gpt-5.1",
            input=PromptText,
            temperature=0.7,
            store=True,
        )

        with open(FileName, "w") as f:
            f.write("\n\n========== NEW RUN ==========\n\n")
            f.write("\n\n========== NEW ITEM ==========\n\n")
            f.write(f"\nTier {TierCode} #1 (Temp = 0.7)\n")
            f.write(Response1.output_text)

        print(Response1.output_text)
        print(f"{TierCode} #1 complete, saved to {FileName}")

        # Second item (reuse instructions, do not store)
        Response2 = client.responses.create(
            model="gpt-5.1",
            previous_response_id=Response1.id,
            input="Write another different unique item based on the same instructions.",
            temperature=0.8,
        )

        with open(FileName, "a") as f:
            f.write("\n\n========== NEW ITEM ==========\n\n")
            f.write(f"\nTier {TierCode} #2 (Temp = 0.8)\n")
            f.write(Response2.output_text)

        print(Response2.output_text)
        print(f"{TierCode} #2 complete, saved to {FileName}")


def RunGemini(Tiers):
    # TODO: implement Gemini calls here
    print("Gemini selected, but RunGemini() is not implemented yet.")


def RunClaude(Tiers):
    # TODO: implement Claude calls here
    print("Claude selected, but RunClaude() is not implemented yet.")


def RunCopilot(Tiers):
    # TODO: implement Copilot calls here
    print("Copilot selected, but RunCopilot() is not implemented yet.")


def main():
    # Make sure Results directory exists
    os.makedirs("Results", exist_ok=True)

    # Build all prompts and tiers once
    Tiers = BuildTiers()

    # Ask which LLM(s) to run
    LlmsSelected = AskLLMs()

    ItemsPerTier = AskItemsPerTier()

    if "GPT" in LlmsSelected:
        RunGpt(Tiers, ItemsPerTier)    if "GPT" in LlmsSelected:
            RunGPT(Tiers)

    if "Gemini" in LlmsSelected:
        RunGemini(Tiers)

    if "Claude" in LlmsSelected:
        RunClaude(Tiers)

    if "Copilot" in LlmsSelected:
        RunCopilot(Tiers)


if __name__ == "__main__":
    main()
