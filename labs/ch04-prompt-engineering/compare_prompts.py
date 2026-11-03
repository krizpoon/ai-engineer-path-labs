# Generated from src/content/chapters (chapter 4) by `npm run labs`. Edit the chapter, not this file.
from baseline import run_baseline

FEW_SHOT = """Classify the customer message into one category:
billing, bug, feature_request or other.

<examples>
<example><message>My card was billed after I cancelled.</message>
<category>billing</category></example>
<example><message>Please support importing clients from CSV.</message>
<category>feature_request</category></example>
<example><message>Where is your company based?</message>
<category>other</category></example>
</examples>

<message>{message}</message>

Reply with the category inside <category> tags and nothing else."""


def prompt_v1(message):
    return "Classify this message: " + message


def prompt_v2(message):
    return FEW_SHOT.format(message=message)


print("v1:", run_baseline(prompt_v1))
print("v2:", run_baseline(prompt_v2))
