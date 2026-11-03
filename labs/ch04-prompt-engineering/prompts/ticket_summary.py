# Generated from src/content/chapters (chapter 4) by `npm run labs`. Edit the chapter, not this file.
from string import Template

VERSION = "ticket-summary/v3"

TEMPLATE = Template("""Summarise this support ticket for the on-call engineer.
They need to decide in under a minute whether to escalate.

<ticket>
$ticket
</ticket>

Reply with:
- One sentence on the problem.
- The customer's plan: $plan.
- "Escalate: yes" or "Escalate: no", with a short reason.""")

def render(ticket: str, plan: str) -> str:
    return TEMPLATE.substitute(ticket=ticket, plan=plan)

# At the call site, log the version next to the request ID so you can trace
# any odd output back to the exact prompt that produced it:
#   logger.info("llm_call", extra={"prompt_version": VERSION, "request_id": response._request_id})
