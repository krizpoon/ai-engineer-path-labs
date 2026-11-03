# Generated from src/content/chapters (chapter 1) by `npm run labs`. Edit the chapter, not this file.
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Explain what an AI Engineer does in two sentences."}
    ],
)

# The reply is a list of content blocks; print the text ones.
for block in response.content:
    if block.type == "text":
        print(block.text)

print(response.stop_reason)  # "end_turn" means it finished; chapter 3 covers the rest
print(response.usage)  # input and output tokens: this is what you pay for
