# AIG_ui.py
# All user interaction: menus, prompts, simple status messages.

import os
import re
from typing import Optional, Tuple, List

from AIG_config import REQUIRED_FILES, PASSAGES_DIR_CANDIDATES


def _FindPassagesDir() -> Optional[str]:
    """
    Return the first passages directory that exists from the candidate list,
    or None if none exist.
    """
    for cand in PASSAGES_DIR_CANDIDATES:
        if os.path.isdir(cand):
            return cand
    return None


def SelectStandard() -> str:
    """
    Look in the current directory for subdirectories whose names look like
    CCSS ELA reading standards, e.g. 'RL 8.1' or 'RI 7.3' or 'RL.8.1'.

    Presents a menu of matching directories and returns the chosen name
    as standard_code, or "" on failure.
    """

    # Pattern: optional leading space, then:
    #   R + (L or I) + optional space/dot + grade (digit, 9-10, or 11-12) + '.' + digit
    pattern = re.compile(r"^ ?R[LI][ .]?(?:\d|9-10|11-12)\.\d+$", re.IGNORECASE)

    candidates: List[str] = []
    for name in os.listdir("."):
        if os.path.isdir(name) and pattern.fullmatch(name):
            candidates.append(name)

    candidates.sort()

    if not candidates:
        print("\nNo standard directories found in the current folder.")
        print("Expected names like 'RL 8.1' or 'RI 7.3'.")
        return ""

    print("\n" * 3 + "═" * 45)
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
    """
    Look in an acceptable 'Passages' directory for .txt files, present a menu,
    and return (passage_file_name, wrapped_passage_text).

    Returns (None, None) on error.
    """

    passages_dir = _FindPassagesDir()

    if passages_dir is None:
        print("\nERROR: No 'Passages' directory found in this standard folder.")
        print("Looked for:")
        for cand in PASSAGES_DIR_CANDIDATES:
            print(f"  • {cand!r}")
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

    print("\n" * 3 + "═" * 45)
    print(f"   Select a Passage (from '{passages_dir}')")
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
                "================== Passage Text =================\n\n"
                + text
                + "\n\n"
            )
            return file_name, passage

        print(f"Please enter a number between 1 and {len(candidates)}.")


def CheckRequiredFiles() -> bool:
    """
    Check if all required files exist before running.

    Returns True if all are present, False otherwise.
    """
    missing_files: List[str] = []
    for file in REQUIRED_FILES:
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
    """
    Ask the user which LLM(s) to run and return a list of identifiers,
    e.g. ["GPT"], ["Claude", "Gemini"], etc.
    """
    print("\n" * 3 + "═" * 45)
    print("   Select an LLM for Item Generation")
    print("═" * 45)
    print("  1) Anthropic's Claude")
    print("  2) Google's Gemini")
    print("  3) Microsoft's Copilot")
    print("  4) OpenAI's GPT")
    print("  5) All of the above")
    print("═" * 45)

    while True:

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
    """
    Ask the user how many items per tier to generate (>=1).
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
