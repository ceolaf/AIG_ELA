# Generate MC Items from a range of LLLMs for a single standard for a single passage.
# Requires the Yes50, Yes100, No50, No100, etc. files to be in the active directory.
# Assumes one such directory per standard per passage. 

import os
import time
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai

# Initialize clients
openai_client = OpenAI()
anthropic_client = Anthropic()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))


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

# Written by ChatGPT and AMH
def RunGPT(Tiers, ItemsPerTier):
    for TierCode, PromptText, FileName in Tiers:

        with open(FileName, "a") as f:
            f.write("\n\n========== NEW RUN GPT ==========\n\n")

        # -------- first item generation --------
        StoreGPTState = (ItemsPerTier > 1)

        Response = openai_client.responses.create(
            model="gpt-5.1",
            input=PromptText,
            temperature=0.7,
            store=StoreGPTState,
        )

        # ----- first item writing to file -----
        with open(FileName, "a") as f:
            f.write("\n\n========== NEW ITEM ==========\n\n")
            f.write(f"\nTier {TierCode} #1 (Temp = 0.7)\n")
            f.write(Response.output_text)

        print(Response.output_text)
        print(f"{TierCode} #1 complete, saved to {FileName}")

        # If only 1 item is needed, skip the rest
        if ItemsPerTier == 1:
            continue

        PrevId = Response.id

        # -------- ITEMS 2..N --------
        for Index in range(2, ItemsPerTier + 1):
            IsLast = (Index == ItemsPerTier)

            # ---- next item generation ---- 
            Response = openai_client.responses.create(
                model="gpt-5.1",
                previous_response_id=PrevId,
                input="Write another different unique item based on the same instructions.",
                temperature=0.8,
                store=not IsLast,
            )

            # ---- write this (i.e., next) item to file ----
            with open(FileName, "a") as f:
                f.write("\n\n========== NEW ITEM ==========\n\n")
                f.write(f"\nTier {TierCode} #{Index} (Temp = 0.8)\n")
                f.write(Response.output_text)

            # ---- write this (i.e., next) item to screen ----
            print(f"{TierCode} #{Index} complete, saved to {FileName}")
            print(Response.output_text)

            # update PrevId only if we are still chaining
            if not IsLast:
                PrevId = Response.id


# Adapted by Gemini and AMH
def RunGemini(Tiers, ItemsPerTier, model_name='gemini-2.5-pro'):

    # Safety settings to block harmful content (can be adjusted)
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    for TierCode, PromptText, FileName in Tiers:
        try:
            # Append a header for this new run
            with open(FileName, "a", encoding="utf-8") as f:
                f.write("\n\n========== NEW RUN (Gemini) ==========\n\n")

            # Initialize the generative model & start chat session
            model = genai.GenerativeModel(model_name)
            chat = model.start_chat(history=[])

            # --- Generation configurations ---
            config_first_item = genai.types.GenerationConfig(temperature=0.7)
            config_next_items = genai.types.GenerationConfig(temperature=0.8)

            # -------- first item generation --------
            print(f"Generating {TierCode} #1 (Temp = 0.7)...")
            
            response = chat.send_message(
                PromptText,
                generation_config=config_first_item,
                safety_settings=safety_settings
            )
            
            # ----- first item writing to file -----
            with open(FileName, "a", encoding="utf-8") as f:
                f.write("\n\n========== NEW ITEM ==========\n\n")
                f.write(f"\nTier {TierCode} #1 (Temp = 0.7)\n")
                f.write(response.text)

            print(response.text)
            print(f"{TierCode} #1 complete, saved to {FileName}")

            # If only 1 item is needed, skip the rest
            if ItemsPerTier == 1:
                continue

            # -------- ITEMS 2..N --------
            for Index in range(2, ItemsPerTier + 1):
                # The prompt for subsequent items
                next_prompt = "Write another different unique item based on the same instructions."
                
                print(f"Generating {TierCode} #{Index} (Temp = 0.8)...")

                # --- next item generation ----
                response = chat.send_message(
                    next_prompt,
                    generation_config=config_next_items,
                    safety_settings=safety_settings
                )
                
                # ---- write this (i.e., next) item to file ----
                with open(FileName, "a", encoding="utf-8") as f:
                    f.write("\n\n========== NEW ITEM ==========\n\n")
                    f.write(f"\nTier {TierCode} #{Index} (Temp = 0.8)\n")
                    f.write(response.text)

                # ---- write this (i.e., next) item to screen ----
                print(f"{TierCode} #{Index} complete, saved to {FileName}")
                print(response.text)
                
                # Add a small delay to respect API rate limits
                time.sleep(1) 

        except Exception as e:
            print(f"An error occurred while processing Tier {TierCode}: {e}")
            print("Moving to the next tier.")
            # Optionally, write the error to the file
            with open(FileName, "a", encoding="utf-8") as f:
                f.write(f"\n\n========== ERROR ==========\n\n")
                f.write(f"An error occurred: {e}\n")
            continue



#Adapted by Claude and AMH
def RunClaude(Tiers, ItemsPerTier):
    for TierCode, PromptText, FileName in Tiers:
        with open(FileName, "a") as f:
            f.write("\n\n========== NEW RUN ==========\n\n")
        
        # -------- first item generation --------
        messages = [{"role": "user", "content": PromptText}]
        
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            temperature=0.7,
            messages=messages
        )
        
        # ----- first item writing to file -----
        response_text = response.content[0].text
        with open(FileName, "a") as f:
            f.write("\n\n========== NEW ITEM ==========\n\n")
            f.write(f"\nTier {TierCode} #1 (Temp = 0.7)\n")
            f.write(response_text)
        print(response_text)
        print(f"{TierCode} #1 complete, saved to {FileName}")
        
        # If only 1 item is needed, skip the rest
        if ItemsPerTier == 1:
            continue
        
        # Add assistant response to conversation history
        messages.append({"role": "assistant", "content": response_text})
        
        # -------- ITEMS 2..N --------
        for Index in range(2, ItemsPerTier + 1):
            # ---- next item generation ----
            messages.append({
                "role": "user", 
                "content": "Write another different unique item based on the same instructions."
            })
            
            response = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0.8,
                messages=messages
            )
            
            response_text = response.content[0].text
            
            # ---- write this item to file ----
            with open(FileName, "a") as f:
                f.write("\n\n========== NEW ITEM ==========\n\n")
                f.write(f"\nTier {TierCode} #{Index} (Temp = 0.8)\n")
                f.write(response_text)
            
            # ---- write this item to screen ----
            print(f"{TierCode} #{Index} complete, saved to {FileName}")
            print(response_text)
            
            # Add assistant response to conversation history
            messages.append({"role": "assistant", "content": response_text})
            
            

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
        RunGPT(Tiers, ItemsPerTier)

    if "Gemini" in LlmsSelected:
        RunGemini(Tiers, ItemsPerTier)

    if "Claude" in LlmsSelected:
        RunClaude(Tiers, ItemsPerTier)

    if "Copilot" in LlmsSelected:
        RunCopilot(Tiers, ItemsPerTier)


if __name__ == "__main__":
    main()
