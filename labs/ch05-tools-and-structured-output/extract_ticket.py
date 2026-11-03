# Generated from src/content/chapters (chapter 5) by `npm run labs`. Edit the chapter, not this file.
from typing import List
from pydantic import BaseModel
import anthropic
from llm_utils import check_stop, UnusableResponse

class SupportTicket(BaseModel):
    customer_name: str
    order_number: str
    category: str          # e.g. "refund", "delivery", "bug"
    urgent: bool
    products: List[str]

client = anthropic.Anthropic()

email = """Hi, this is Jane Doe. Order 1182 arrived with a cracked
mug and the teapot is missing. I need it before Saturday!"""

response = client.messages.parse(
    model="claude-opus-5-5",
    max_tokens=2000,
    messages=[{"role": "user", "content": f"Extract the ticket details:\n\n{email}"}],
    output_format=SupportTicket,
)

check_stop(response)              # raises on max_tokens, refusal, ...
ticket = response.parsed_output   # a validated SupportTicket
if ticket is None:
    raise UnusableResponse("No parsed output")
print(ticket.order_number, ticket.urgent, ticket.products)
