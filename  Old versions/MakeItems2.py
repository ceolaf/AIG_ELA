from openai import OpenAI

client = OpenAI()


# Read your prompt components
with open("Standard.txt") as f:
    Standard = f.read()

with open("Yes50.txt") as f:
    Yes50 = f.read()

with open("Yes100.txt") as f:
    Yes100 = f.read()
    
with open("No50.txt") as f:
    No50 = f.read()

with open("No100.txt") as f:
    No100 = f.read()

with open("Misconceptions.txt") as f:
    Misconceptions = f.read()

with open("LBIDAT.md") as f:
    LBIDAT = f.read()

with open("Standard Code.md") as f:
    StandardCode = f.read()


# read text

with open("Passage.txt") as f:
    Text1 = f.read()


# Tier 2a

Prompt2a = f"""

You are an expert content development professional writing high quality items for large scale assessments for 8th grade based on the following passage. Please write two multiple choice items (if you can) aligned to {Standard} using the following literary passage. 

· The key (i.e, the correct answer option] should be marked with an “*”.
· Please include rationales for each answer option that lay out the steps or reasoning that would lead to each response.
· If you revise the item, please make sure to include the full final version at the end.

The passage:
{Text1}

"""

# Tier 2b

Prompt2b = f"""

You are an expert content development professional writing high quality items for large scale assessments for 8th grade based on the following passage. Please write two multiple choice items (if you can) aligned to {Standard} using the following literary passage. 

· The key (i.e, the correct answer option] should be marked with an “*”.
· Please include rationales for each answer option that lay out the steps or reasoning that would lead to each response.
· If you revise the item, please make sure to include the full final version at the end.

Your goal is for each item to score well on the LBIDAT criteria, whose complete text is included below.

The passage:
{Text1}

The LBIDAT:
{LBIDAT}
"""

# Tier 3a

Prompt3a = f"""

You are an expert content development professional writing high quality items for large scale assessments for 8th grade based on the following passage. Please write two multiple choice items (if you can) aligned to {Standard} using the following literary passage. That standard means, {Yes50}

· The key (i.e, the correct answer option] should be marked with an “*”.
· Please include rationales for each answer option that lay out the steps or reasoning that would lead to each response.
· If you revise the item, please make sure to include the full final version at the end.

The passage:
{Text1}


"""

# Tier 3b

Prompt3b = f"""

You are an expert content development professional writing high quality items for large scale assessments for 8th grade based on the following passage. Please write two multiple choice items (if you can) aligned to {Standard} using the following literary passage. That standard means, {Yes50}

· The key (i.e, the correct answer option] should be marked with an “*”.
· Please include rationales for each answer option that lay out the steps or reasoning that would lead to each response.
· If you revise the item, please make sure to include the full final version at the end.

Your goal is for each item to score well on the LBIDAT criteria, whose complete text is included below.

The passage:
{Text1}

The LBIDAT:
{LBIDAT}
"""

# Tier 4a

Prompt4a = f"""

You are an expert content development professional writing high quality items for large scale assessments for 8th grade based on the following passage. Please write two multiple choice items (if you can) aligned to {Standard} using the following literary passage. That standard means, {Yes100}

· The key (i.e, the correct answer option] should be marked with an “*”.
· Please include rationales for each answer option that lay out the steps or reasoning that would lead to each response.
· If you revise the item, please make sure to include the full final version at the end.

The passage:
{Text1}


"""


# Tier 4b

Prompt4b = f"""

You are an expert content development professional writing high quality items for large scale assessments for 8th grade based on the following passage. Please write two multiple choice items (if you can) aligned to {Standard} using the following literary passage. That standard means, {Yes100}

· The key (i.e, the correct answer option] should be marked with an “*”.
· Please include rationales for each answer option that lay out the steps or reasoning that would lead to each response.
· If you revise the item, please make sure to include the full final version at the end.

Your goal is for each item to score well on the LBIDAT criteria, whose complete text is included below.

The passage:
{Text1}

The LBIDAT:
{LBIDAT}
"""


# Tier 5a

Prompt5a = f"""

You are an expert content development professional writing high quality items for large scale assessments for 8th grade based on the following passage. Please write two multiple choice items (if you can) aligned to {Standard} using the following literary passage. That standard means, {Yes100} However, {No50}

· The key (i.e, the correct answer option] should be marked with an “*”.
· Please include rationales for each answer option that lay out the steps or reasoning that would lead to each response.
· If you revise the item, please make sure to include the full final version at the end.

The passage:
{Text1}


"""



# Tier 5b

Prompt5b = f"""

You are an expert content development professional writing high quality items for large scale assessments for 8th grade based on the following passage. Please write two multiple choice items (if you can) aligned to {Standard} using the following literary passage. That standard means, {Yes100} However, {No50}

· The key (i.e, the correct answer option] should be marked with an “*”.
· Please include rationales for each answer option that lay out the steps or reasoning that would lead to each response.
· If you revise the item, please make sure to include the full final version at the end.

Your goal is for each item to score well on the LBIDAT criteria, whose complete text is included below.

The passage:
{Text1}

The LBIDAT:
{LBIDAT}
"""



# Tier 6a

Prompt6a = f"""

You are an expert content development professional writing high quality items for large scale assessments for 8th grade based on the following passage. Please write two multiple choice items (if you can) aligned to {Standard} using the following literary passage. That standard means, {Yes100} However, {No100}

· The key (i.e, the correct answer option] should be marked with an “*”.
· Please include rationales for each answer option that lay out the steps or reasoning that would lead to each response.
· If you revise the item, please make sure to include the full final version at the end.

The passage:
{Text1}


"""


# Tier 66

Prompt6b = f"""

You are an expert content development professional writing high quality items for large scale assessments for 8th grade based on the following passage. Please write two multiple choice items (if you can) aligned to {Standard} using the following literary passage. That standard means, {Yes100} However, {No100}

· The key (i.e, the correct answer option] should be marked with an “*”.
· Please include rationales for each answer option that lay out the steps or reasoning that would lead to each response.
· If you revise the item, please make sure to include the full final version at the end.

Your goal is for each item to score well on the LBIDAT criteria, whose complete text is included below.

The passage:
{Text1}

The LBIDAT:
{LBIDAT}


"""


# Tier 7a

Prompt7a = f"""

You are an expert content development professional writing high quality items for large scale assessments for 8th grade based on the following passage. Please write two multiple choice items (if you can) aligned to {Standard} using the following literary passage. That standard means, {Yes100} However, {No100}

Distractors may be based upon the following misconceptions or mistakes, or other errors with the *targeted* cognition. 
{Misconceptions}

· The key (i.e, the correct answer option] should be marked with an “*”.
· Please include rationales for each answer option that lay out the steps or reasoning that would lead to each response.
· If you revise the item, please make sure to include the full final version at the end.

The passage:
{Text1}


"""


# Tier 7b

Prompt7b = f"""

You are an expert content development professional writing high quality items for large scale assessments for 8th grade based on the following passage. Please write two multiple choice items (if you can) aligned to {Standard} using the following literary passage. That standard means, {Yes100} However, {No100}

Distractors may be based upon the following misconceptions or mistakes, or other errors with the *targeted* cognition. 
{Misconceptions}

· The key (i.e, the correct answer option] should be marked with an “*”.
· Please include rationales for each answer option that lay out the steps or reasoning that would lead to each response.
· If you revise the item, please make sure to include the full final version at the end.

Your goal is for each item to score well on the LBIDAT criteria, whose complete text is included below.

The passage:
{Text1}

The LBIDAT:
{LBIDAT}
"""

# Create lists and list of tuples

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

# Generating & saving new items

# Loop over Tiers to make calls and save results

for TierCode, PromptText, FileName in Tiers:
    # First item: full instructions, store=True so we can use previous_response_id
    Response1 = client.responses.create(
        model="gpt-5.1",
        input=PromptText,
        temperature=0.7,
        store=True,      # <-- we store THIS one
    )

    with open(FileName, "w") as f:
        f.write("\n\n========== NEW RUN ==========\n\n")
        f.write("\n\n========== NEW ITEM ==========\n\n")
        f.write(Response1.output_text)

    print(Response1.output_text)
    print(f"{TierCode} #1 complete, saved to {FileName}")

    # Second item: use previous_response_id but DO NOT store
    Response2 = client.responses.create(
        model="gpt-5.1",
        previous_response_id=Response1.id,
        input="Write another different unique item based on the same instructions.",
        temperature=0.8,
        # NO store=True here — this resets context for the next tier
    )

    with open(FileName, "a") as f:
        f.write("\n\n========== NEW ITEM ==========\n\n")
        f.write(Response2.output_text)

    print(Response2.output_text)
    print(f"{TierCode} #2 complete, saved to {FileName}")
