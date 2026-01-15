"""
RTD Central Tenet (or Mantra):
Valid items elicit evidence of the targeted cognition for the range of typical test takers.

This script exists to experiment with AIG *only* insofar as it helps us generate, 
refine, or study items that remain valid by that standard. Efficiency gains that reduce 
item validity are out of scope and not acceptable.
"""

# AIG_config.py
# Central configuration for model names, file requirements, prompts, directories,
# temperatures, and service-specific settings.

from typing import Final, List, Dict


# ---------------------------------------------------------------------------
#  Model names (intended canonical names)
# ---------------------------------------------------------------------------

GPT_MODEL: Final[str] = "gpt-5.1"
CLAUDE_MODEL: Final[str] = "claude-opus-4-1-20250805"
GEMINI_MODEL: Final[str] = "gemini-3-pro-preview"


# ---------------------------------------------------------------------------
#  Directory names (intended) + fallback candidates
# ---------------------------------------------------------------------------

# Intended correct name
PASSAGES_DIR: Final[str] = "Passages"

# Tolerated alternatives (filesystem quirks, legacy folders, typos)
PASSAGES_DIR_CANDIDATES: Final[List[str]] = [
    "Passages",     # correct
    " Passages",    # leading-space variant that sometimes appears
    "Texts",
    " Texts",
]


# ---------------------------------------------------------------------------
#  Required files for a valid standard directory
# ---------------------------------------------------------------------------

REQUIRED_FILES: Final[List[str]] = [
    "Standard.txt",
    "Yes50.txt",
    "Yes100.txt",
    "No50.txt",
    "No100.txt",
    "Misconceptions.txt",
    "LBIDAT.md",
]


# ---------------------------------------------------------------------------
#  Result directory naming
# ---------------------------------------------------------------------------

# So you can uniformly build: f"{standard_code}{RESULTS_SUFFIX}"
RESULTS_SUFFIX: Final[str] = " Results"


# ---------------------------------------------------------------------------
#  Generation behavior (temperatures, messages)
# ---------------------------------------------------------------------------

FIRST_ITEM_TEMP: Final[float] = 0.7
NEXT_ITEM_TEMP: Final[float] = 0.8

FOLLOWUP_PROMPT: Final[str] = (
    "Write another different unique item based on the same instructions."
)


# ---------------------------------------------------------------------------
#  Gemini: safety categories
# ---------------------------------------------------------------------------

GEMINI_SAFETY_SETTINGS: Final[List[Dict[str, str]]] = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]


# ---------------------------------------------------------------------------
#  Copilot: timeouts and authentication scopes
# ---------------------------------------------------------------------------

# HTTP timeouts for Graph requests
COPILOT_PING_TIMEOUT: Final[float] = 10.0     # startup test
COPILOT_CHAT_TIMEOUT: Final[float] = 60.0     # item generation

# OAuth scopes required for the Copilot Chat API
COPILOT_SCOPES: Final[List[str]] = [
    "Sites.Read.All",
    "Mail.Read",
    "People.Read.All",
    "OnlineMeetingTranscript.Read.All",
    "Chat.Read",
    "ChannelMessage.Read.All",
    "ExternalItem.Read.All",
]
