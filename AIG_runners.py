# AIG_runners.py
# All LLM-specific code: configuration, clients, and runner functions.

import os
import time
from datetime import datetime
from typing import Optional, Tuple, Dict, List

import httpx
from azure.identity import DeviceCodeCredential
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic

from AIG_output import PrintToFileAndScreen
from AIG_config import (
    GPT_MODEL,
    CLAUDE_MODEL,
    GEMINI_MODEL,
    FIRST_ITEM_TEMP,
    NEXT_ITEM_TEMP,
    FOLLOWUP_PROMPT,
    GEMINI_SAFETY_SETTINGS,
    COPILOT_PING_TIMEOUT,
    COPILOT_CHAT_TIMEOUT,
    COPILOT_SCOPES,
)

# Initialize clients for the LLMs that use simple API keys/env config
openai_client = OpenAI()
anthropic_client = Anthropic()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
# Copilot auth is handled lazily via InitCopilotAuth / TestCopilotStartup


# ---------------------------------------------------------------------------
#  GPT runner
# ---------------------------------------------------------------------------

def RunGPT(
    tiers: List[tuple[str, str, str]],
    item_per_tier: int,
    passage_name: str,
) -> None:
    """
    Run OpenAI GPT on all tiers, generating item_per_tier items per tier.
    """

    # Quick startup test
    try:
        openai_client.responses.create(
            model=GPT_MODEL,
            input="ping",
            temperature=0,
        )
    except Exception as e:
        print("GPT failed startup test:", e)
        return

    print("\n\n********************* Starting GPT tiers... ")

    for tier_code, prompt_text, file_name in tiers:

        # Append a header for this new run
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_name, "a", encoding="utf-8") as f:
            f.write(
                f"\n\n\n=============== NEW RUN GPT - {timestamp} ===============\n\n"
            )

        try:
            # -------- first item generation --------
            print(f"\n\nGenerating {tier_code} (GPT) #1 (Temp = {FIRST_ITEM_TEMP})...\n")

            store_GPT_state = item_per_tier > 1

            start_time = time.time()
            response = openai_client.responses.create(  # This is the LLM call
                model=GPT_MODEL,
                input=prompt_text,
                temperature=FIRST_ITEM_TEMP,
                store=store_GPT_state,
            )
            end_time = time.time()
            elapsed = end_time - start_time

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

            if item_per_tier == 1:
                continue

            prev_ID = response.id

            # -------- ITEMS 2..N --------
            for index in range(2, item_per_tier + 1):
                is_last = index == item_per_tier

                print(
                    f"\n\nGenerating {tier_code} (GPT) #{index} "
                    f"(Temp = {NEXT_ITEM_TEMP})..."
                )

                start_time = time.time()
                response = openai_client.responses.create(  # This is the LLM call
                    model=GPT_MODEL,
                    previous_response_id=prev_ID,
                    input=FOLLOWUP_PROMPT,
                    temperature=NEXT_ITEM_TEMP,
                    store=not is_last,
                )
                end_time = time.time()
                elapsed = end_time - start_time

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

                if not is_last:
                    prev_ID = response.id

        except Exception as e:
            print(f"An error occurred while processing Tier {tier_code} (GPT): {e}")
            with open(file_name, "a", encoding="utf-8") as f:
                f.write("\n\n========== ERROR ==========\n\n")
                f.write(
                    f"An error occurred while processing this tier (GPT): {e}\n"
                )
            continue


# ---------------------------------------------------------------------------
#  Gemini runner
# ---------------------------------------------------------------------------

def RunGemini(
    tiers: List[tuple[str, str, str]],
    item_per_tier: int,
    passage_name: str,
) -> None:
    """
    Run Google's Gemini on all tiers.
    """

    # Quick startup test
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        model.generate_content("ping")
    except Exception as e:
        print("Gemini failed startup test:", e)
        return

    print("\n\n********************* Starting Gemini tiers... ")

    for tier_code, prompt_text, file_name in tiers:
        try:
            # Append a header for this new run
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(file_name, "a", encoding="utf-8") as f:
                f.write(
                    f"\n\n\n=============== NEW RUN (Gemini) - {timestamp} "
                    f"==============="
                    f"\n\n"
                )

            # Initialize the generative model & start chat session
            model = genai.GenerativeModel(GEMINI_MODEL)
            chat = model.start_chat(history=[])

            # --- Generation configurations ---
            config_first_item = genai.types.GenerationConfig(
                temperature=FIRST_ITEM_TEMP
            )
            config_next_items = genai.types.GenerationConfig(
                temperature=NEXT_ITEM_TEMP
            )

            # -------- first item generation --------
            print(
                f"Generating {tier_code} (Gemini) #1 (Temp = {FIRST_ITEM_TEMP})..."
            )

            start_time = time.time()
            response = chat.send_message(  # This is the LLM call
                prompt_text,
                generation_config=config_first_item,
                safety_settings=GEMINI_SAFETY_SETTINGS,
            )
            end_time = time.time()
            elapsed = end_time - start_time

            # FIXED: Check if metadata exists, then access attributes directly
            if response.usage_metadata:
                in_tokens = response.usage_metadata.prompt_token_count
                out_tokens = response.usage_metadata.candidates_token_count
            else:
                in_tokens = 0
                out_tokens = 0

            PrintToFileAndScreen(
                "Gemini",
                tier_code,
                1,
                response.text,
                file_name,
                passage_name,
                elapsed,
                in_tokens,
                out_tokens,
            )

            if item_per_tier == 1:
                continue

            # -------- ITEMS 2..N --------
            for index in range(2, item_per_tier + 1):
                print(
                    f"Generating {tier_code} (Gemini) #{index} "
                    f"(Temp = {NEXT_ITEM_TEMP})..."
                )

                start_time = time.time()
                response = chat.send_message(  # This is the LLM call
                    FOLLOWUP_PROMPT,
                    generation_config=config_next_items,
                    safety_settings=GEMINI_SAFETY_SETTINGS,
                )
                end_time = time.time()
                elapsed = end_time - start_time

                # FIXED: Check if metadata exists, then access attributes directly
                if response.usage_metadata:
                    in_tokens = response.usage_metadata.prompt_token_count
                    out_tokens = response.usage_metadata.candidates_token_count
                else:
                    in_tokens = 0
                    out_tokens = 0

                PrintToFileAndScreen(
                    "Gemini",
                    tier_code,
                    index,
                    response.text,
                    file_name,
                    passage_name,
                    elapsed,
                    in_tokens,
                    out_tokens,
                )

                time.sleep(1)

        except Exception as e:
            print(f"An error occurred while processing Tier {tier_code} (Gemini): {e}")
            print("Moving to the next tier.")
            with open(file_name, "a", encoding="utf-8") as f:
                f.write(f"\n\n========== ERROR ==========\n\n")
                f.write(f"An error occurred: {e}\n")
            continue

# ---------------------------------------------------------------------------
#  Claude runner
# ---------------------------------------------------------------------------

def RunClaude(
    tiers: List[tuple[str, str, str]],
    item_per_tier: int,
    passage_name: str,
) -> None:
    """
    Run Anthropic Claude on all tiers.
    """

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

    print("\n\n********************* Starting Claude tiers... ")

    for tier_code, prompt_text, file_name in tiers:

        # Append a header for this new run
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_name, "a", encoding="utf-8") as f:
            f.write(
                f"\n\n\n=============== NEW RUN (Claude) - {timestamp} "
                f"==============="
                f"\n\n"
            )

        try:
            # -------- first item generation --------
            print(
                f"Generating {tier_code} (Claude) #1 (Temp = {FIRST_ITEM_TEMP})..."
            )

            messages: List[Dict[str, str]] = [
                {"role": "user", "content": prompt_text}
            ]

            start_time = time.time()
            response = anthropic_client.messages.create(  # This is the LLM call
                model=CLAUDE_MODEL,
                max_tokens=4096,
                temperature=FIRST_ITEM_TEMP,
                messages=messages,
            )
            end_time = time.time()
            elapsed = end_time - start_time

            response_text = response.content[0].text

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

            if item_per_tier == 1:
                continue

            # Add assistant response to conversation history
            messages.append({"role": "assistant", "content": response_text})

            # -------- ITEMS 2..N --------
            for index in range(2, item_per_tier + 1):
                print(
                    f"Generating {tier_code} (Claude) #{index} "
                    f"(Temp = {NEXT_ITEM_TEMP})..."
                )

                messages.append(
                    {
                        "role": "user",
                        "content": FOLLOWUP_PROMPT,
                    }
                )

                start_time = time.time()
                response = anthropic_client.messages.create(  # This is the LLM call
                    model=CLAUDE_MODEL,
                    max_tokens=4096,
                    temperature=NEXT_ITEM_TEMP,
                    messages=messages,
                )
                end_time = time.time()
                elapsed = end_time - start_time

                response_text = response.content[0].text

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

                messages.append({"role": "assistant", "content": response_text})

        except Exception as e:
            print(f"An error occurred while processing Tier {tier_code} (Claude): {e}")
            with open(file_name, "a", encoding="utf-8") as f:
                f.write("\n\n========== ERROR ==========\n\n")
                f.write(
                    f"An error occurred while processing this tier (Claude): {e}\n"
                )
            continue


# ---------------------------------------------------------------------------
#  Copilot helpers
# ---------------------------------------------------------------------------

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

        token = credentials.get_token(*COPILOT_SCOPES).token

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
        with httpx.Client(timeout=COPILOT_PING_TIMEOUT) as client:
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


def CreateCopilotConversation(
    client: httpx.Client,
    base_url: str,
    headers: Dict[str, str],
    tier_code: str,
) -> Optional[str]:
    """
    Create a new Copilot conversation for the given tier and return its ID.
    """
    conv_resp = client.post(
        f"{base_url}/copilot/conversations",
        headers=headers,
        json={},
    )

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

def RunCopilot(
    tiers: List[tuple[str, str, str]],
    item_per_tier: int,
    passage_name: str,
) -> None:
    """
    Run Microsoft Copilot (via Graph) on all tiers.
    """

    startup = TestCopilotStartup()
    if startup is None:
        print("Skipping Copilot runs due to startup error.")
        return

    base_url, headers = startup

    print("\n\n********************* Starting Copilot tiers... ")

    with httpx.Client(timeout=COPILOT_CHAT_TIMEOUT) as client:

        for tier_code, prompt_text, file_name in tiers:

            conversation_id = CreateCopilotConversation(
                client=client,
                base_url=base_url,
                headers=headers,
                tier_code=tier_code,
            )
            if conversation_id is None:
                continue

            # Header for this run
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(file_name, "a", encoding="utf-8") as f:
                f.write(
                    f"\n\n=============== NEW RUN (Copilot) - {timestamp}  "
                    f"==============="
                    f"\n\n"
                )

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

            if item_per_tier == 1:
                continue

            # -------- ITEMS 2..N --------
            for index in range(2, item_per_tier + 1):
                print(f"Generating {tier_code} (Copilot) #{index}...")

                start_time = time.time()
                next_text = send_chat(FOLLOWUP_PROMPT)
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
