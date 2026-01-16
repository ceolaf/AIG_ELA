# Generate MC Items from a range of LLLMs for a single standard for a single passage.
# Requires the yes50, yes100, no50, no100, etc. files to be in the active directory.
# Assumes one such directory per standard per passage.


# ======================
# Standard library imports
# ======================
import os
import re
import time
from datetime import datetime
from typing import Optional, Tuple, Dict

# ======================
# Third-party imports
# ======================
import httpx
from azure.identity import DeviceCodeCredential
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic

# ======================
# (No local imports)
# ======================



# ==== Model configuration ====
GPT_MODEL = "gpt-5.1"
CLAUDE_MODEL = "claude-opus-4-1-20250805"
GEMINI_MODEL = "gemini-3-pro-preview"

# Initialize clients
openai_client = OpenAI()
anthropic_client = Anthropic()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
# Note: Copilot client initialized in RunCopilot() due to interactive authentication requirement


# ---------------------------------------------------------------------------
#  Standard and passage selection
# ---------------------------------------------------------------------------

def SelectStandard() -> str:
    # Look in the current directory for subdirectories whose names look like
    # CCSS ELA reading standards, e.g. 'RL 8.1' or 'RI 7.3' or 'RL.8.1'.
    # Presents a menu of matching directories and returns the chosen name
    # as standard_code.

    # Pattern: R + (L or I) + space or dot + number.number

    pattern = re.compile(r"^ ?R[LI][ .]?(?:\d|9-10|11-12)\.\d+$", re.IGNORECASE)

    # Find subdirectories matching the pattern
    candidates: list[str] = []
    for name in os.listdir("."):
        if os.path.isdir(name) and pattern.fullmatch(name):
            candidates.append(name)

    candidates.sort()

    if not candidates:
        print("\nNo standard directories found in the current folder.")
        print("Expected names like 'RL 8.1' or 'RI 7.3'.")
        return ""

    print("\n" + "═" * 45)
    print("   Select a Standard (Directory)")
    print("═" * 45)
    for idx, name in enumerate(candidates, start=1):
        print(f"  {idx}) {name}")
    print("═" * 45)

    while True:
        choice = input(f"Enter your choice (1–{len(candidates)}): ").strip()
        if not choice.isdigit():
            print("Please enter a number.")
            continue

        index = int(choice)
        if 1 <= index <= len(candidates):
            standard_code = candidates[index - 1]
            print(f"\nYou selected: {standard_code}")
            return standard_code

        print(f"Please enter a number between 1 and {len(candidates)}.")


def SelectPassage() -> Tuple[Optional[str], Optional[str]]:
    # Look in the 'Passages' subdirectory for .txt files, present a menu,
    # and return the selected passage text wrapped the same way you used
    # to do in BuildTiers().

    passages_dir = "Passages"

    if not os.path.isdir(passages_dir):
        print("\nERROR: No 'Passages' directory found in this standard folder.")
        print("Please create a 'Passages' subdirectory and add .txt files.")
        return None, None

    # Find all .txt files inside Passages
    candidates: list[str] = []
    for name in os.listdir(passages_dir):
        full_path = os.path.join(passages_dir, name)
        if os.path.isfile(full_path) and name.lower().endswith(".txt"):
            candidates.append(name)

    candidates.sort()

    if not candidates:
        print("\nERROR: No .txt files found in the 'Passages' directory.")
        print("Please add at least one .txt file.")
        return None, None

    print("\n" + "═" * 45)
    print("   Select a Passage")
    print("═" * 45)
    for idx, name in enumerate(candidates, start=1):
        print(f"  {idx}) {name}")
    print("═" * 45)

    while True:
        choice = input(f"Enter your choice (1–{len(candidates)}): ").strip()
        if not choice.isdigit():
            print("Please enter a number.")
            continue

        index = int(choice)
        if 1 <= index <= len(candidates):
            file_name = candidates[index - 1]
            full_path = os.path.join(passages_dir, file_name)
            print(f"\nYou selected passage file: {file_name}")

            with open(full_path) as f:
                text = f.read()

            # Match your previous style for the passage variable
            passage = (
                "================== passage Text =================\n\n"
                + text
                + "\n\n"
            )
            return file_name, passage

        print(f"Please enter a number between 1 and {len(candidates)}.")


# ---------------------------------------------------------------------------
#  File checks and prompt construction
# ---------------------------------------------------------------------------

def CheckRequiredFiles() -> bool:
    """Check if all required files exist before running."""
    required_files: list[str] = [
        "Standard.txt",
        "Yes50.txt",
        "Yes100.txt",
        "No50.txt",
        "No100.txt",
        "Misconceptions.txt",
        "LBIDAT.md",
    ]

    missing_files: list[str] = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print("\n" + "═" * 45)
        print("   ERROR: Missing Required Files")
        print("═" * 45)
        print("The following files are missing:")
        for file in missing_files:
            print(f"  • {file}")
        print("═" * 45)
        print("Please add these files to the directory and try again.")
        return False

    print("✓ All required files found")
    return True


def AskLLMs() -> list[str]:
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

        user_choice = input("Enter your choice (1–5): ").strip()

        match user_choice:
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


def AskItemsPerTier() -> int:
    while True:
        answer = input("How many items per tier do you want? (1 or more): ").strip()
        if not answer.isdigit():
            print("Please enter a whole number like 1, 2, 3...")
            continue

        count = int(answer)
        if count < 1:
            print("Please enter a number 1 or greater.")
            continue

        return count


def BuildTiers(standard_code: str, passage: str) -> list[tuple[str, str, str]]:
    # Read the prompt components

    with open("Standard.txt") as f:
        standard = f.read().strip()

    prompt_part1 = (
        "You are an expert content development professional writing high quality "
        "items for large scale assessments for 8th grade based on the following "
        "passage. Please write a unique multiple choice items (if you can) aligned "
        f"to {standard} using the following literary passage."
    )

    with open("Yes50.txt") as f:
        yes50 = "That standard means, " + f.read()

    with open("Yes100.txt") as f:
        yes100 = "That standard means, " + f.read()

    with open("No50.txt") as f:
        no50 = "However, " + f.read()

    with open("No100.txt") as f:
        no100 = "However, " + f.read()

    with open("Misconceptions.txt") as f:
        misconceptions = (
            "\n\nDistractors may be based upon the following misconceptions or "
            "mistakes-- or upon other errors with the *targeted* cognition.\n"
            + f.read()
        )

    prompt_part2 = (
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

    # Build each prompt
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
    prompt_7b = prompt_part1 + yes100 + no100 + prompt_part2 + misconceptions + LBIDAT + passage

    # Create the tiers list (tier code, prompt text, filename)
    tiers: list[tuple[str, str, str]] = [
        ("2a", prompt_2a, f"{standard_code} Results/{standard_code} Tier 2a Item Output.txt"),
        ("2b", prompt_2b, f"{standard_code} Results/{standard_code} Tier 2b Item Output.txt"),
        ("3a", prompt_3a, f"{standard_code} Results/{standard_code} Tier 3a Item Output.txt"),
        ("3b", prompt_3b, f"{standard_code} Results/{standard_code} Tier 3b Item Output.txt"),
        ("4a", prompt_4a, f"{standard_code} Results/{standard_code} Tier 4a Item Output.txt"),
        ("4b", prompt_4b, f"{standard_code} Results/{standard_code} Tier 4b Item Output.txt"),
        ("5a", prompt_5a, f"{standard_code} Results/{standard_code} Tier 5a Item Output.txt"),
        ("5b", prompt_5b, f"{standard_code} Results/{standard_code} Tier 5b Item Output.txt"),
        ("6a", prompt_6a, f"{standard_code} Results/{standard_code} Tier 6a Item Output.txt"),
        ("6b", prompt_6b, f"{standard_code} Results/{standard_code} Tier 6b Item Output.txt"),
        ("7a", prompt_7a, f"{standard_code} Results/{standard_code} Tier 7a Item Output.txt"),
        ("7b", prompt_7b, f"{standard_code} Results/{standard_code} Tier 7b Item Output.txt"),
    ]

    return tiers


# ---------------------------------------------------------------------------
#  Output helper
# ---------------------------------------------------------------------------

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

    if index == 1:
        temperature = " (temp=0.7)"
    else:
        temperature = " (temp=0.8)"
    if LLM == "Copilot":
        temperature = ""

    total_tokens = input_tokens + output_tokens

    with open(file_name, "a") as f:
        f.write("\n\n\n================= NEW ITEM =================")
        f.write(f"\nPassage: {passage_name}")
        f.write(
            f"\nTier {tier_code} ({LLM}) #{index}{temperature}. "
            f"({elapsed:.2f} secs). ({input_tokens} + {output_tokens} = {total_tokens} total tokens)\n\n"
        )
        f.write(response)

    print("\n\n================= NEW ITEM =================")
    print(f"\nTier {tier_code} ({LLM}) #{index}{temperature}. ({elapsed:.2f} secs)\n\n")
    print(response)
    print(f"\n\nTier {tier_code} #{index} complete, saved to {file_name}\n")


# ---------------------------------------------------------------------------
#  LLM runners
# ---------------------------------------------------------------------------


# Written by ChatGPT and AMH
def RunGPT(
    tiers: list[tuple[str, str, str]],
    item_per_tier: int,
    passage_name: str,
) -> None:

    # Quick startup test
    try:
        openai_client.responses.create(
            model=GPT_MODEL,
            input="ping",
            temperature=0
        )
    except Exception as e:
    print("GPT failed startup test:", e)
    return
    
    print(f"\n\n********************* Starting GPT tiers... ")

    for tier_code, prompt_text, file_name in tiers:

        # Append a header for this new run
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_name, "a") as f:
            f.write(
                f"\n\n\n=============== NEW RUN GPT - {timestamp} ===============\n\n"
            )

        try:
            # -------- first item generation --------
            print(f"\n\nGenerating {tier_code} (GPT) #1 (Temp = 0.7)...\n")

            store_GPT_state = item_per_tier > 1

            start_time = time.time()
            response = openai_client.responses.create(        # This is the LLM call
                model=GPT_MODEL,
                input=prompt_text,
                temperature=0.7,
                store=store_GPT_state,
            )
            end_time = time.time()
            elapsed = end_time - start_time

            # Call AMH's printing/filing function
            PrintToFileAndScreen(
                "GPT",
                tier_code,
                1,
                response.output_text,
                file_name,
                passage_name,
                elapsed,
                response.usage.input_tokens,
                response.usage.output_tokens,
            )

            # If only 1 item is needed, skip the rest
            if item_per_tier == 1:
                continue

            prev_ID = response.id

            # -------- ITEMS 2..N --------
            for index in range(2, item_per_tier + 1):
                is_last = index == item_per_tier

                print(f"\n\nGenerating {tier_code} (GPT) #{index} (Temp = 0.8)...")

                # ---- next item generation ----
                start_time = time.time()
                response = openai_client.responses.create(    # This is the LLM call
                    model=GPT_MODEL,
                    previous_response_id=prev_ID,
                    input=(
                        "Write another different unique item based on the same "
                        "instructions."
                    ),
                    temperature=0.8,
                    store=not is_last,
                )
                end_time = time.time()
                elapsed = end_time - start_time

                # Call AMH's printing/filing function
                PrintToFileAndScreen(
                    "GPT",
                    tier_code,
                    index,
                    response.output_text,
                    file_name,
                    passage_name,
                    elapsed,
                    response.usage.input_tokens,
                    response.usage.output_tokens,
                )

                # update prev_ID only if we are still chaining
                if not is_last:
                    prev_ID = response.id

        except Exception as e:
            print(f"An error occurred while processing Tier {tier_code} (GPT): {e}")
            with open(file_name, "a", encoding="utf-8") as f:
                f.write("\n\n========== ERROR ==========\n\n")
                f.write(
                    f"An error occurred while processing this tier (GPT): {e}\n"
                )
            # Move on to the next tier
            continue


# Adapted by Gemini and AMH
def RunGemini(
    tiers: list[tuple[str, str, str]],
    item_per_tier: int,
    passage_name: str,
) -> None:

    # Quick startup test
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        model.generate_content("ping")
    except Exception as e:
        print("Gemini failed startup test:", e)
        return

    print(f"\n\n********************* Starting Gemini tiers... ")

    # Safety settings to block harmful content (can be adjusted)
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    for tier_code, prompt_text, file_name in tiers:
        try:

            # Append a header for this new run
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(file_name, "a") as f:
                f.write(
                    f"\n\n\n=============== NEW RUN (Gemini) - {timestamp} "
                    f"==============="
                    f"\n\n"
                )

            # Initialize the generative model & start chat session
            model = genai.GenerativeModel(GEMINI_MODEL)
            chat = model.start_chat(history=[])

            # --- Generation configurations ---
            config_first_item = genai.types.GenerationConfig(temperature=0.7)
            config_next_items = genai.types.GenerationConfig(temperature=0.8)

            # -------- first item generation --------
            print(f"Generating {tier_code} (Gemini) #1 (Temp = 0.7)...")

            start_time = time.time()
            response = chat.send_message(                # This is the LLM call
                prompt_text,
                generation_config=config_first_item,
                safety_settings=safety_settings,
            )
            end_time = time.time()
            elapsed = end_time - start_time

            # Call AMH's printing/filing function
            PrintToFileAndScreen(
                "Gemini",
                tier_code,
                1,
                response.text,
                file_name,
                passage_name,
                elapsed,
                (response.usage_metadata or {}).get("prompt_token_count", 0),
                (response.usage_metadata or {}).get("candidates_token_count", 0),
            )
            # That crap above is because gemini sometimes just doesn't supply the token counts

            # If only 1 item is needed, skip the rest
            if item_per_tier == 1:
                continue

            # -------- ITEMS 2..N --------
            for index in range(2, item_per_tier + 1):

                print(f"Generating {tier_code} (Gemini) #{index} (Temp = 0.8)...")

                # The prompt for subsequent items
                next_prompt = (
                    "Write another different unique item based on the same "
                    "instructions."
                )

                # --- next item generation ----
                start_time = time.time()
                response = chat.send_message(               # This is the LLM call
                    next_prompt,
                    generation_config=config_next_items,
                    safety_settings=safety_settings,
                )
                end_time = time.time()
                elapsed = end_time - start_time

                # Call AMH's printing/filing function
                PrintToFileAndScreen(
                    "Gemini",
                    tier_code,
                    index,
                    response.text,
                    file_name,
                    passage_name,
                    elapsed,
                    (response.usage_metadata or {}).get("prompt_token_count", 0),
                    (response.usage_metadata or {}).get("candidates_token_count", 0),
                )

                # Add a small delay to respect API rate limits
                time.sleep(1)

        except Exception as e:
            print(f"An error occurred while processing Tier {tier_code}: {e}")
            print("Moving to the next tier.")
            # Optionally, write the error to the file
            with open(file_name, "a", encoding="utf-8") as f:
                f.write(f"\n\n========== ERROR ==========\n\n")
                f.write(f"An error occurred: {e}\n")
            continue


#Adapted by Claude and AMH
def RunClaude(
    tiers: list[tuple[str, str, str]],
    item_per_tier: int,
    passage_name: str,
) -> None:

    # Quick startup test
    try:
        anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1,
            temperature=0,
            messages=[{"role": "user", "content": "ping"}],
        )
    except Exception as e:
        print("Claude failed startup test:", e)
        return
    
    print(f"\n\n********************* Starting Claude tiers... ")

    for tier_code, prompt_text, file_name in tiers:

        # Append a header for this new run
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_name, "a") as f:
            f.write(
                f"\n\n\n=============== NEW RUN (Claude) - {timestamp} "
                f"==============="
                f"\n\n"
            )

        try:
            # -------- first item generation --------
            print(f"Generating {tier_code} (Claude) #1 (Temp = 0.7)...")

            messages = [{"role": "user", "content": prompt_text}]

            start_time = time.time()
            response = anthropic_client.messages.create(      # This is the LLM call
                model=CLAUDE_MODEL,
                max_tokens=4096,
                temperature=0.7,
                messages=messages,
            )
            end_time = time.time()
            elapsed = end_time - start_time

            response_text = response.content[0].text

            # Call AMH's printing/filing function
            PrintToFileAndScreen(
                "Claude",
                tier_code,
                1,
                response_text,
                file_name,
                passage_name,
                elapsed,
                response.usage.input_tokens,
                response.usage.output_tokens,
            )

            # If only 1 item is needed, skip the rest
            if item_per_tier == 1:
                continue

            # Add assistant response to conversation history
            messages.append({"role": "assistant", "content": response_text})

            # -------- ITEMS 2..N --------
            for index in range(2, item_per_tier + 1):
                # ---- next item generation ----
                print(f"Generating {tier_code} (Claude) #{index} (Temp = 0.8)...")

                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Write another different unique item based on the same "
                            "instructions."
                        ),
                    }
                )

                start_time = time.time()
                response = anthropic_client.messages.create(  # This is the LLM call
                    model=CLAUDE_MODEL,
                    max_tokens=4096,
                    temperature=0.8,
                    messages=messages,
                )
                end_time = time.time()
                elapsed = end_time - start_time

                response_text = response.content[0].text

                # Call AMH's printing/filing function
                PrintToFileAndScreen(
                    "Claude",
                    tier_code,
                    index,
                    response_text,
                    file_name,
                    passage_name,
                    elapsed,
                    response.usage.input_tokens,
                    response.usage.output_tokens,
                )

                # Add assistant response to conversation history
                messages.append({"role": "assistant", "content": response_text})

        except Exception as e:
            print(f"An error occurred while processing Tier {tier_code} (Claude): {e}")
            with open(file_name, "a", encoding="utf-8") as f:
                f.write("\n\n========== ERROR ==========\n\n")
                f.write(
                    f"An error occurred while processing this tier (Claude): {e}\n"
                )
            # Move on to the next tier
            continue
            

# ---------------------------------------------------------------------------
#  Copilot helpers
#  Separated out to make RunCopilot cleaner. Moves Copilot's messiness aside.
# ---------------------------------------------------------------------------

def TestCopilotStartup() -> Optional[Tuple[str, Dict[str, str]]]:
    """
    Quick startup test for Copilot.

    Returns (base_url, headers) if successful, or None on failure.
    """
    try:
        auth = InitCopilotAuth()
        if auth is None:
            print("Copilot failed startup test: auth initialization failed.")
            return None

        base_url, headers = auth

        # Minimal "ping": try to create an empty conversation
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                f"{base_url}/copilot/conversations",
                headers=headers,
                json={},
            )

        if resp.status_code != 201:
            print("Copilot failed startup test: conversation creation failed.")
            print("Status:", resp.status_code)
            print("Raw response:", resp.text)
            return None

        return base_url, headers

    except Exception as e:
        print("Copilot failed startup test:", e)
        return None
        
        
def InitCopilotAuth() -> Optional[Tuple[str, Dict[str, str]]]:
    """
    Initialize authentication for Copilot / Graph and return (base_url, headers).

    Adapted by Copilot and AMH, auth cleanup assisted by GPT-5.1.
    """
    try:
        credentials = DeviceCodeCredential(
            tenant_id=os.environ.get("AZURE_TENANT_ID"),
            client_id=os.environ.get("AZURE_CLIENT_ID"),
        )

        # These scopes match the docs for the Copilot Chat API
        token = credentials.get_token(
            "Sites.Read.All",
            "Mail.Read",
            "People.Read.All",
            "OnlineMeetingTranscript.Read.All",
            "Chat.Read",
            "ChannelMessage.Read.All",
            "ExternalItem.Read.All",
        ).token

    except Exception as e:
        print("\nERROR initializing Copilot authentication.")
        print(f"Details: {e}")
        return None

    base_url = "https://graph.microsoft.com/beta"
    headers: Dict[str, str] = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    return base_url, headers


def CreateCopilotConversation(
    client: httpx.Client,
    base_url: str,
    headers: Dict[str, str],
    tier_code: str,
) -> Optional[str]:
    """
    Create a new Copilot conversation for the given tier and return its ID.

    Adapted by Copilot and AMH, refactoring assisted by GPT-5.1.
    """
    conv_resp = client.post(
        f"{base_url}/copilot/conversations",
        headers=headers,
        json={},
    )

    # Only log and skip THIS tier if there is an error
    if conv_resp.status_code != 201:
        print(f"\nERROR creating conversation for tier {tier_code}.")
        print("Status code:", conv_resp.status_code)
        print("Raw response:", conv_resp.text)
        return None

    conv_data = conv_resp.json()
    conversation_id = conv_data.get("id")
    if not conversation_id:
        print(f"\nERROR: No conversation ID returned for tier {tier_code}.")
        print("Raw response:", conv_resp.text)
        return None

    return conversation_id


# ---------------------------------------------------------------------------
#  Copilot runner
# ---------------------------------------------------------------------------

# Adapted by Copilot and AMH, structure/typing cleanup assisted by GPT-5.1
def RunCopilot(
    tiers: list[tuple[str, str, str]],
    item_per_tier: int,
    passage_name: str,
) -> None:

    # Quick startup test
    startup = TestCopilotStartup()
    if startup is None:
        print("Skipping Copilot runs due to startup error.")
        return

    base_url, headers = startup

    print(f"\n\n********************* Starting Copilot tiers... ")

    with httpx.Client(timeout=60.0) as client:

        for tier_code, prompt_text, file_name in tiers:

            # Create a new conversation for this tier
            conversation_id = CreateCopilotConversation(
                client=client,
                base_url=base_url,
                headers=headers,
                tier_code=tier_code,
            )
            if conversation_id is None:
                # Error already logged; skip this tier
                continue

            # Write your normal header (unchanged)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(file_name, "a") as f:
                f.write(
                    f"\n\n=============== NEW RUN (Copilot) - {timestamp}  "
                    f"==============="
                    f"\n\n"
                )

            # ---- helper ----
            def send_chat(prompt: str) -> Optional[str]:
                chat_payload = {
                    "message": {"text": prompt},
                    "locationHint": {"timeZone": "America/New_York"},
                }

                chat_resp = client.post(
                    f"{base_url}/copilot/conversations/{conversation_id}/chat",
                    headers=headers,
                    json=chat_payload,
                )

                # SUCCESS — no debug printing
                if chat_resp.status_code == 200:
                    data = chat_resp.json()
                    messages = data.get("messages")
                    if not messages:
                        print(f"ERROR: No messages returned (tier {tier_code}).")
                        print("Raw JSON:", chat_resp.text)
                        return None
                    return messages[-1].get("text", "")

                # ERROR — print raw JSON for diagnosis
                print(f"ERROR during chat send (tier {tier_code}).")
                print("Status:", chat_resp.status_code)
                print("Raw JSON:", chat_resp.text)
                return None

            # -------- first item --------
            print(f"Generating {tier_code} (Copilot) #1...")

            start_time = time.time()
            first_text = send_chat(prompt_text)  # This is the LLM call
            end_time = time.time()
            elapsed = end_time - start_time

            if first_text is None:
                print(f"Skipping tier {tier_code} due to chat error.")
                continue

            PrintToFileAndScreen(
                "Copilot",
                tier_code,
                1,
                first_text,
                file_name,
                passage_name,
                elapsed,
                0,
                0,
            )

            # If only 1 item requested
            if item_per_tier == 1:
                continue

            # -------- ITEMS 2..N --------
            for index in range(2, item_per_tier + 1):
                print(f"Generating {tier_code} (Copilot) #{index}...")

                start_time = time.time()
                next_text = send_chat(
                    "Write another different unique item based on the same "
                    "instructions."
                )
                end_time = time.time()
                elapsed = end_time - start_time

                if next_text is None:
                    print(
                        f"Stopping tier {tier_code} after #{index-1} "
                        f"due to chat error."
                    )
                    break

                PrintToFileAndScreen(
                    "Copilot",
                    tier_code,
                    index,
                    next_text,
                    file_name,
                    passage_name,
                    elapsed,
                    0,
                    0,
                )
                time.sleep(1)


# ---------------------------------------------------------------------------
#  Main entry point
# ---------------------------------------------------------------------------

def main() -> None:

    # Pick the standard from available directories one level down
    standard_code = SelectStandard()
    if not standard_code:
        # Nothing selected or no valid directories
        return

    # Let the user select a passage from Passages/
    passage_name, passage_text = SelectPassage()
    if passage_text is None:         # User couldn't select a passage or something went wrong
        return

    # Change into that standard's directory
    os.chdir(standard_code)

    # Check for required files first
    if not CheckRequiredFiles():
        return  # Exit if files are missing

    # Create a dynamic results directory based on the standard code
    results_dir = f"{standard_code} Results"
    os.makedirs(results_dir, exist_ok=True)

    # Build all prompts and tiers once
    tiers = BuildTiers(standard_code, passage_text)

    # Ask which LLM(s) to run
    LLMs_selected = AskLLMs()

    item_per_tier = AskItemsPerTier()

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
