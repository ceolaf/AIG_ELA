"""
Generate multiple-choice items from a range of LLMs for a single standard and passage.

Directory assumptions (same as original script):

- Current working directory contains subdirectories named for standards, e.g.:
    "RL 8.1", "RI 7.3", "RL.8.1", etc.

- Within the current working directory (root), there is a "Passages/" directory
  containing .txt files with passage text.

- Within each standard directory (e.g., "RL 8.1"), the following files exist:
    - Standard.txt
    - Yes50.txt
    - Yes100.txt
    - No50.txt
    - No100.txt
    - Misconceptions.txt
    - LBIDAT.md

- For each standard directory, results are written into:
    "<standard_code> Results/<standard_code> Tier X Item Output.txt"
"""

from __future__ import annotations

import os
import re
import time
from datetime import datetime
from typing import List, Tuple, Optional

import google.generativeai as genai  # Gemini
import httpx                         # Copilot
from anthropic import Anthropic      # Claude
from azure.identity import DeviceCodeCredential  # Copilot
from openai import OpenAI            # GPT


# ==== Model configuration ====
GPT_MODEL = "gpt-5.1"
CLAUDE_MODEL = "claude-opus-4-1-20250805"
GEMINI_MODEL = "gemini-3-pro-preview"

# Initialize clients
openai_client = OpenAI()
anthropic_client = Anthropic()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
# Note: Copilot client is initialized inside run_copilot() because of interactive auth.


# ---------------------------------------------------------------------------
#  Standard & passage selection
# ---------------------------------------------------------------------------

def select_standard() -> str:
    """
    Scan the current directory for subdirectories whose names look like CCSS
    ELA reading standards (e.g. 'RL 8.1', 'RI 7.3', 'RL.8.1').

    Presents a numbered menu and returns the chosen directory name as
    the standard code. Returns an empty string if none selected.
    """
    # Pattern: R + (L or I) + optional space or dot + grade (digit/9-10/11-12) + '.' + standard
    pattern = re.compile(r"^R[LI][ .]?(?:\d|9-10|11-12)\.\d+$", re.IGNORECASE)

    candidates: List[str] = [
        name
        for name in os.listdir(".")
        if os.path.isdir(name) and pattern.fullmatch(name)
    ]
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


def select_passage() -> Tuple[Optional[str], Optional[str]]:
    """
    Look in the root-level 'Passages' subdirectory for .txt files,
    present a menu, and return:

        (passage_filename, passage_text_wrapped)

    If there is an error or no passage is selected, returns (None, None).
    """
    passages_dir = "Passages"

    if not os.path.isdir(passages_dir):
        print("\nERROR: No 'Passages' directory found in this folder.")
        print("Please create a 'Passages' subdirectory and add .txt files.")
        return None, None

    candidates: List[str] = []
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

            with open(full_path, encoding="utf-8") as f:
                text = f.read()

            passage = (
                "================== passage Text =================\n\n"
                + text
                + "\n\n"
            )
            return file_name, passage

        print(f"Please enter a number between 1 and {len(candidates)}.")


# ---------------------------------------------------------------------------
#  File checks & prompt building
# ---------------------------------------------------------------------------

def check_required_files() -> bool:
    """
    Check if all required configuration files exist in the current directory.

    Returns True if all are present, False otherwise.
    """
    required_files = [
        "Standard.txt",
        "Yes50.txt",
        "Yes100.txt",
        "No50.txt",
        "No100.txt",
        "Misconceptions.txt",
        "LBIDAT.md",
    ]

    missing_files = [file for file in required_files if not os.path.exists(file)]

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


def ask_llms() -> List[str]:
    """
    Ask the user which LLM(s) to use for item generation.

    Returns a list containing any of: "Claude", "Gemini", "Copilot", "GPT".
    """
    options = {
        "1": ["Claude"],
        "2": ["Gemini"],
        "3": ["Copilot"],
        "4": ["GPT"],
        "5": ["Claude", "Gemini", "Copilot", "GPT"],
    }

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
        if user_choice in options:
            return options[user_choice]

        print("\nInvalid choice. Please enter a number from 1 to 5.")


def ask_items_per_tier() -> int:
    """
    Ask the user how many items to generate per tier.

    Must be an integer >= 1.
    """
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


def build_tiers(standard_code: str, passage: str) -> List[Tuple[str, str, str]]:
    """
    Build the prompts for each tier of item generation.

    Returns a list of tuples:
        (tier_code, prompt_text, output_file_path)
    """
    with open("Standard.txt", encoding="utf-8") as f:
        standard = f.read().strip()

    prompt_part1 = (
        "You are an expert content development professional writing high quality "
        "items for large scale assessments for 8th grade based on the following "
        "passage. Please write a unique multiple choice item (if you can) aligned "
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
        "· The key (i.e, the correct answer option] should be marked with an “*”.\n\n"
        "· The item should have three distractors.\n\n"
        "· Please include rationales for each answer option that lay out the steps or "
        "reasoning that would lead to each response.\n\n"
        "· If you revise the item, please make sure to include the full final "
        "version at the end.\n\n"
    )

    with open("LBIDAT.md", encoding="utf-8") as f:
        lbidat = (
            "**** Your goal is for each item to score well on the LBIDAT criteria, "
            "whose complete text is included below. ***\n\n"
            + f.read()
        )

    # Build each prompt
    prompt_2a = prompt_part1 + prompt_part2 + passage
    prompt_2b = prompt_part1 + prompt_part2 + lbidat + passage
    prompt_3a = prompt_part1 + yes50 + prompt_part2 + passage
    prompt_3b = prompt_part1 + yes50 + prompt_part2 + lbidat + passage
    prompt_4a = prompt_part1 + yes100 + prompt_part2 + passage
    prompt_4b = prompt_part1 + yes100 + prompt_part2 + lbidat + passage
    prompt_5a = prompt_part1 + yes100 + no50 + prompt_part2 + passage
    prompt_5b = prompt_part1 + yes100 + no50 + prompt_part2 + lbidat + passage
    prompt_6a = prompt_part1 + yes100 + no100 + prompt_part2 + passage
    prompt_6b = prompt_part1 + yes100 + no100 + prompt_part2 + lbidat + passage
    prompt_7a = prompt_part1 + yes100 + no100 + prompt_part2 + misconceptions + passage
    prompt_7b = (
        prompt_part1 + yes100 + no100 + prompt_part2 + misconceptions + lbidat + passage
    )

    results_dir = f"{standard_code} Results"

    tiers: List[Tuple[str, str, str]] = [
        ("2a", prompt_2a, os.path.join(results_dir, f"{standard_code} Tier 2a Item Output.txt")),
        ("2b", prompt_2b, os.path.join(results_dir, f"{standard_code} Tier 2b Item Output.txt")),
        ("3a", prompt_3a, os.path.join(results_dir, f"{standard_code} Tier 3a Item Output.txt")),
        ("3b", prompt_3b, os.path.join(results_dir, f"{standard_code} Tier 3b Item Output.txt")),
        ("4a", prompt_4a, os.path.join(results_dir, f"{standard_code} Tier 4a Item Output.txt")),
        ("4b", prompt_4b, os.path.join(results_dir, f"{standard_code} Tier 4b Item Output.txt")),
        ("5a", prompt_5a, os.path.join(results_dir, f"{standard_code} Tier 5a Item Output.txt")),
        ("5b", prompt_5b, os.path.join(results_dir, f"{standard_code} Tier 5b Item Output.txt")),
        ("6a", prompt_6a, os.path.join(results_dir, f"{standard_code} Tier 6a Item Output.txt")),
        ("6b", prompt_6b, os.path.join(results_dir, f"{standard_code} Tier 6b Item Output.txt")),
        ("7a", prompt_7a, os.path.join(results_dir, f"{standard_code} Tier 7a Item Output.txt")),
        ("7b", prompt_7b, os.path.join(results_dir, f"{standard_code} Tier 7b Item Output.txt")),
    ]

    return tiers


# ---------------------------------------------------------------------------
#  Common output helper
# ---------------------------------------------------------------------------

def print_to_file_and_screen(
    llm_name: str,
    tier_code: str,
    index: int,
    response_text: str,
    file_name: str,
    passage_name: str,
    elapsed: float,
    input_tokens: int,
    output_tokens: int,
) -> None:
    """
    Append the item output to the given file and print it to the console.

    Adds metadata such as LLM name, tier, index, temperature, elapsed seconds,
    and token usage.
    """
    if index == 1:
        temperature_suffix = " (temp=0.7)"
    else:
        temperature_suffix = " (temp=0.8)"

    if llm_name == "Copilot":
        # We don't explicitly set temperature for Copilot; suppress suffix.
        temperature_suffix = ""

    total_tokens = input_tokens + output_tokens

    header = (
        "\n\n\n================= NEW ITEM ================="
        f"\nPassage: {passage_name}"
        f"\nTier {tier_code} ({llm_name}) #{index}{temperature_suffix}. "
        f"({elapsed:.2f} secs). "
        f"({input_tokens} + {output_tokens} = {total_tokens} total tokens)\n\n"
    )

    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "a", encoding="utf-8") as f:
        f.write(header)
        f.write(response_text)

    print("\n\n================= NEW ITEM =================")
    print(f"\nTier {tier_code} ({llm_name}) #{index}{temperature_suffix}. ({elapsed:.2f} secs)\n")
    print(response_text)
    print(f"\n\nTier {tier_code} #{index} complete, saved to {file_name}\n")


# ---------------------------------------------------------------------------
#  GPT
# ---------------------------------------------------------------------------

def run_gpt(
    tiers: List[Tuple[str, str, str]],
    items_per_tier: int,
    passage_name: str,
) -> None:
    """Run OpenAI GPT over all tiers."""
    print("\n\n********************* Starting GPT tiers... ")

    for tier_code, prompt_text, file_name in tiers:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_name, "a", encoding="utf-8") as f:
            f.write(
                f"\n\n\n=============== NEW RUN GPT - {timestamp} ===============\n\n"
            )

        # First item
        print(f"\n\nGenerating {tier_code} (GPT) #1 (Temp = 0.7)...\n")
        store_state = items_per_tier > 1

        start_time = time.time()
        response = openai_client.responses.create(
            model=GPT_MODEL,
            input=prompt_text,
            temperature=0.7,
            store=store_state,
        )
        elapsed = time.time() - start_time

        print_to_file_and_screen(
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

        if items_per_tier == 1:
            continue

        prev_id = response.id

        # Items 2..N
        for index in range(2, items_per_tier + 1):
            is_last = index == items_per_tier
            print(f"\n\nGenerating {tier_code} (GPT) #{index} (Temp = 0.8)...")

            start_time = time.time()
            response = openai_client.responses.create(
                model=GPT_MODEL,
                previous_response_id=prev_id,
                input="Write another different unique item based on the same instructions.",
                temperature=0.8,
                store=not is_last,
            )
            elapsed = time.time() - start_time

            print_to_file_and_screen(
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

            if not is_last:
                prev_id = response.id


# ---------------------------------------------------------------------------
#  Gemini
# ---------------------------------------------------------------------------

def run_gemini(
    tiers: List[Tuple[str, str, str]],
    items_per_tier: int,
    passage_name: str,
) -> None:
    """Run Google Gemini over all tiers."""
    print("\n\n********************* Starting Gemini tiers... ")

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
    ]

    for tier_code, prompt_text, file_name in tiers:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(file_name, "a", encoding="utf-8") as f:
                f.write(
                    f"\n\n\n=============== NEW RUN (Gemini) - {timestamp} ===============\n\n"
                )

            model = genai.GenerativeModel(GEMINI_MODEL)
            chat = model.start_chat(history=[])

            config_first = genai.types.GenerationConfig(temperature=0.7)
            config_next = genai.types.GenerationConfig(temperature=0.8)

            # First item
            print(f"Generating {tier_code} (Gemini) #1 (Temp = 0.7)...")
            start_time = time.time()
            response = chat.send_message(
                prompt_text,
                generation_config=config_first,
                safety_settings=safety_settings,
            )
            elapsed = time.time() - start_time

            usage = response.usage_metadata or {}
            print_to_file_and_screen(
                "Gemini",
                tier_code,
                1,
                response.text,
                file_name,
                passage_name,
                elapsed,
                usage.get("prompt_token_count", 0),
                usage.get("candidates_token_count", 0),
            )

            if items_per_tier == 1:
                continue

            # Items 2..N
            for index in range(2, items_per_tier + 1):
                print(f"Generating {tier_code} (Gemini) #{index} (Temp = 0.8)...")

                start_time = time.time()
                response = chat.send_message(
                    "Write another different unique item based on the same instructions.",
                    generation_config=config_next,
                    safety_settings=safety_settings,
                )
                elapsed = time.time() - start_time

                usage = response.usage_metadata or {}
                print_to_file_and_screen(
                    "Gemini",
                    tier_code,
                    index,
                    response.text,
                    file_name,
                    passage_name,
                    elapsed,
                    usage.get("prompt_token_count", 0),
                    usage.get("candidates_token_count", 0),
                )

                time.sleep(1)  # be gentle with the API

        except Exception as exc:  # noqa: BLE001
            print(f"An error occurred while processing Tier {tier_code}: {exc}")
            print("Moving to the next tier.")
            with open(file_name, "a", encoding="utf-8") as f:
                f.write("\n\n========== ERROR ==========\n\n")
                f.write(f"An error occurred: {exc}\n")
            continue


# ---------------------------------------------------------------------------
#  Claude
# ---------------------------------------------------------------------------

def run_claude(
    tiers: List[Tuple[str, str, str]],
    items_per_tier: int,
    passage_name: str,
) -> None:
    """Run Anthropic Claude over all tiers."""
    print("\n\n********************* Starting Claude tiers... ")

    for tier_code, prompt_text, file_name in tiers:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_name, "a", encoding="utf-8") as f:
            f.write(
                f"\n\n\n=============== NEW RUN (Claude) - {timestamp} ===============\n\n"
            )

        messages = [{"role": "user", "content": prompt_text}]

        # First item
        print(f"Generating {tier_code} (Claude) #1 (Temp = 0.7)...")
        start_time = time.time()
        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            temperature=0.7,
            messages=messages,
        )
        elapsed = time.time() - start_time
        response_text = response.content[0].text

        print_to_file_and_screen(
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

        if items_per_tier == 1:
            continue

        messages.append({"role": "assistant", "content": response_text})

        # Items 2..N
        for index in range(2, items_per_tier + 1):
            print(f"Generating {tier_code} (Claude) #{index} (Temp = 0.8)...")

            messages.append(
                {
                    "role": "user",
                    "content": "Write another different unique item based on the same instructions.",
                }
            )

            start_time = time.time()
            response = anthropic_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4096,
                temperature=0.8,
                messages=messages,
            )
            elapsed = time.time() - start_time
            response_text = response.content[0].text

            print_to_file_and_screen(
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

            messages.append({"role": "assistant", "content": response_text})


# ---------------------------------------------------------------------------
#  Copilot
# ---------------------------------------------------------------------------

def run_copilot(
    tiers: List[Tuple[str, str, str]],
    items_per_tier: int,
    passage_name: str,
) -> None:
    """Run Microsoft Copilot via Graph API over all tiers."""
    print("\n\n********************* Starting Copilot tiers... ")

    credentials = DeviceCodeCredential(
        tenant_id=os.environ.get("AZURE_TENANT_ID"),
        client_id=os.environ.get("AZURE_CLIENT_ID"),
    )

    token = credentials.get_token(
        "Sites.Read.All",
        "Mail.Read",
        "People.Read.All",
        "OnlineMeetingTranscript.Read.All",
        "Chat.Read",
        "ChannelMessage.Read.All",
        "ExternalItem.Read.All",
    ).token

    base_url = "https://graph.microsoft.com/beta"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=60.0) as client:
        for tier_code, prompt_text, file_name in tiers:
            # Create conversation for this tier
            conv_resp = client.post(
                f"{base_url}/copilot/conversations",
                headers=headers,
                json={},
            )

            if conv_resp.status_code != 201:
                print(f"\nERROR creating conversation for tier {tier_code}.")
                print("Status code:", conv_resp.status_code)
                print("Raw response:", conv_resp.text)
                continue

            conv_data = conv_resp.json()
            conversation_id = conv_data.get("id")
            if not conversation_id:
                print(f"\nERROR: No conversation ID returned for tier {tier_code}.")
                print("Raw response:", conv_resp.text)
                continue

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(file_name, "a", encoding="utf-8") as f:
                f.write(
                    f"\n\n=============== NEW RUN (Copilot) - {timestamp}  ===============\n\n"
                )

            def send_chat(prompt: str) -> Optional[str]:
                """
                Send a message to Copilot and return the last text response,
                or None on error.
                """
                chat_payload = {
                    "message": {"text": prompt},
                    "locationHint": {"timeZone": "America/New_York"},
                }

                chat_resp = client.post(
                    f"{base_url}/copilot/conversations/{conversation_id}/chat",
                    headers=headers,
                    json=chat_payload,
                )

                if chat_resp.status_code == 200:
                    data = chat_resp.json()
                    messages = data.get("messages")
                    if not messages:
                        print(f"ERROR: No messages returned (tier {tier_code}).")
                        print("Raw JSON:", chat_resp.text)
                        return None
                    return messages[-1].get("text", "")

                print(f"ERROR during chat send (tier {tier_code}).")
                print("Status:", chat_resp.status_code)
                print("Raw JSON:", chat_resp.text)
                return None

            # First item
            print(f"Generating {tier_code} (Copilot) #1...")
            start_time = time.time()
            first_text = send_chat(prompt_text)
            elapsed = time.time() - start_time

            if first_text is None:
                print(f"Skipping tier {tier_code} due to chat error.")
                continue

            print_to_file_and_screen(
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

            if items_per_tier == 1:
                continue

            # Items 2..N
            for index in range(2, items_per_tier + 1):
                print(f"Generating {tier_code} (Copilot) #{index}...")

                start_time = time.time()
                next_text = send_chat(
                    "Write another different unique item based on the same instructions."
                )
                elapsed = time.time() - start_time

                if next_text is None:
                    print(
                        f"Stopping tier {tier_code} after #{index - 1} due to chat error."
                    )
                    break

                print_to_file_and_screen(
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
#  Main
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Orchestrate standard selection, passage selection, prompt building,
    and running the selected LLMs over all tiers.
    """
    # Pick the standard from available directories one level down
    standard_code = select_standard()
    if not standard_code:
        return

    # Select passage from root-level Passages/
    passage_name, passage_text = select_passage()
    if passage_text is None:
        return

    # Move into the selected standard's directory
    os.chdir(standard_code)

    # Check for required files
    if not check_required_files():
        return

    # Ensure results directory exists
    results_dir = f"{standard_code} Results"
    os.makedirs(results_dir, exist_ok=True)

    # Build prompts/tiers
    tiers = build_tiers(standard_code, passage_text)

    # Choose LLMs and item count
    selected_llms = ask_llms()
    items_per_tier = ask_items_per_tier()

    if "GPT" in selected_llms:
        run_gpt(tiers, items_per_tier, passage_name)

    if "Gemini" in selected_llms:
        run_gemini(tiers, items_per_tier, passage_name)

    if "Claude" in selected_llms:
        run_claude(tiers, items_per_tier, passage_name)

    if "Copilot" in selected_llms:
        run_copilot(tiers, items_per_tier, passage_name)


# ---------------------------------------------------------------------------
#  Backwards-compatible aliases for original function names
# ---------------------------------------------------------------------------

# If you were importing these from elsewhere, they still exist:
SelectStandard = select_standard
SelectPassage = select_passage
CheckRequiredFiles = check_required_files
AskLLMs = ask_llms
AskItemsPerTier = ask_items_per_tier
BuildTiers = build_tiers
PrintToFileAndScreen = print_to_file_and_screen
RunGPT = run_gpt
RunGemini = run_gemini
RunClaude = run_claude
RunCopilot = run_copilot


if __name__ == "__main__":
    main()
