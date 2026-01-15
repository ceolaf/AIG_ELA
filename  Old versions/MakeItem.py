from openai import OpenAI

client = OpenAI()

standard = "RL.8.1"   # You can change this later

prompt = f"""
Write one multiple-choice item aligned to the Common Core standard {standard}.
The item should be minimal and self-contained.
Just write:

- a question
- four answer options labeled A–D
- mark the correct answer with an asterisk before it (*A, *B, etc.)

No explanation. No extra text.
"""

response = client.responses.create(
    model="gpt-5.1",
    input=prompt
)

# Save to a file:
with open("item_output.txt", "w") as f:
    f.write(response.output_text)

print(response.output_text)
