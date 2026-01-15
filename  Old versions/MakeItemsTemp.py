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

# Create arrays

TierCodes = ["2a","2b","3a","3b","4a","4b","5a","5b","6a","6b","7a","7b"]

Prompts = [
    ("2a", Prompt2a),
    ("2b", Prompt2b),
    ("3a", Prompt3a),
    ("3b", Prompt3b),
    ("4a", Prompt4a),
    ("4b", Prompt4b),
    ("5a", Prompt5a),
    ("5b", Prompt5b),
    ("6a", Prompt6a),
    ("6b", Prompt6b),
    ("7a", Prompt7a),
    ("7b", Prompt7b),
]


# List of (tierCode, filenameString)
Filenames = [
    (tier, f"Results/{StandardCode} Tier {tier} Item Output.txt")
    for tier in TierCodes
]

# Turn the first two into dicts so we can look up by tier code
PromptDict   = dict(Prompts)
FilenameDict = dict(Filenames)


# Tiers = list of tuples: (tierCode, promptString, filenameString)
Tiers = [
    (tier, PromptDict[tier], FilenameDict[tier])
    for tier in TierCodes
]


# Generation & Saving

##Tier 2a

response = client.responses.create(
    model="gpt-5.1",
    input=Prompt2a,
    temperature=0.7,
    store=True,
)

with open("Results/RL 8.4 Tier 2a Item Output.txt", "a") as f:
    f.write("\n\n========== NEW RUN ==========\n\n")
    f.write(response.output_text)

print(response.output_text)

responseC = client.responses.create(
    model="gpt-5.1",
    previous_response_id=responseB.id,
    input="Write another different unique item based on the same instructions.",
    temperature=0.8,
)

with open("Results/RL 8.4 Tier 2a Item Output.txt", "a") as f:
    f.write("\n\n========== NEW RUN ==========\n\n")
    f.write(response.output_text)

print(response.output_text)



##Tier 2b
response = client.responses.create(
    model="gpt-5.1",
    input=Prompt2b
    temperature=0.8,
    store=True,
)

with open("Results/RL 8.4 Tier 2b Item Output.txt", "a") as f:
    f.write("\n\n========== NEW RUN ==========\n\n")
    f.write(response.output_text)

print(response.output_text)

##Tier 3a
response = client.responses.create(
    model="gpt-5.1",
    input=Prompt3a
    temperature=0.8,
    store=True,
)

with open("Results/RL 8.4 Tier 3a Item Output.txt", "a") as f:
    f.write("\n\n========== NEW RUN ==========\n\n")
    f.write(response.output_text)

print(response.output_text)

##Tier 3b
response = client.responses.create(
    model="gpt-5.1",
    input=Prompt3b
    temperature=0.8,
    store=True,
)

with open("Results/RL 8.4 Tier 3b Item Output.txt", "a") as f:
    f.write("\n\n========== NEW RUN ==========\n\n")
    f.write(response.output_text)

print(response.output_text)

##Tier 4a
response = client.responses.create(
    model="gpt-5.1",
    input=Prompt4a
    temperature=0.8,
    store=True,
)

with open("Results/RL 8.4 Tier 4a Item Output.txt", "a") as f:
    f.write("\n\n========== NEW RUN ==========\n\n")
    f.write(response.output_text)

print(response.output_text)

##Tier 4b
response = client.responses.create(
    model="gpt-5.1",
    input=Prompt4b
    temperature=0.8,
    store=True,
)

with open("Results/RL 8.4 Tier 4b Item Output.txt", "a") as f:
    f.write("\n\n========== NEW RUN ==========\n\n")
    f.write(response.output_text)

print(response.output_text)

##Tier 5a
response = client.responses.create(
    model="gpt-5.1",
    input=Prompt5a
    temperature=0.8,
    store=True,
)

with open("Results/RL 8.4 Tier 5a Item Output.txt", "a") as f:
    f.write("\n\n========== NEW RUN ==========\n\n")
    f.write(response.output_text)

print(response.output_text)

##Tier 5b
response = client.responses.create(
    model="gpt-5.1",
    input=Prompt5b
    temperature=0.8,
    store=True,
)

with open("Results/RL 8.4 Tier 5b Item Output.txt", "a") as f:
    f.write("\n\n========== NEW RUN ==========\n\n")
    f.write(response.output_text)

print(response.output_text)

##Tier 6a
response = client.responses.create(
    model="gpt-5.1",
    input=Prompt6a
    temperature=0.8,
    store=True,
)

with open("Results/RL 8.4 Tier 6a Item Output.txt", "a") as f:
    f.write("\n\n========== NEW RUN ==========\n\n")
    f.write(response.output_text)

print(response.output_text)

##Tier 6b
response = client.responses.create(
    model="gpt-5.1",
    input=Prompt6b
    temperature=0.8,
    store=True,
)

with open("Results/RL 8.4 Tier 6b Item Output.txt", "a") as f:
    f.write("\n\n========== NEW RUN ==========\n\n")
    f.write(response.output_text)

print(response.output_text)

##Tier 7a
response = client.responses.create(
    model="gpt-5.1",
    input=Prompt7a
    temperature=0.8,
    store=True,
)

with open("Results/RL 8.4 Tier 7a Item Output.txt", "a") as f:
    f.write("\n\n========== NEW RUN ==========\n\n")
    f.write(response.output_text)

print(response.output_text)

##Tier 7b
response = client.responses.create(
    model="gpt-5.1",
    input=Prompt7b
    temperature=0.8,
    store=True,
)

with open("Results/RL 8.4 Tier 7b Item Output.txt", "a") as f:
    f.write("\n\n========== NEW RUN ==========\n\n")
    f.write(response.output_text)

print(response.output_text)

