# Generated from src/content/chapters (chapter 8) by `npm run labs`. Edit the chapter, not this file.
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("team-docs")

DOCS = {
    "deploys": "Deploys go out from main via CI. Staging: run 'make deploy-staging'.",
    "oncall": "On-call rotates weekly. Page the secondary if the primary is silent for 15 min.",
}

@mcp.tool()
def search_docs(query: str) -> str:
    """Search the team handbook. Returns every page that mentions the query."""
    hits = [f"## {name}\n{text}" for name, text in DOCS.items() if query.lower() in text.lower()]
    return "\n\n".join(hits) or "No matching pages."

@mcp.resource("docs://{name}")
def get_doc(name: str) -> str:
    """One handbook page by name."""
    return DOCS.get(name, "No such page.")

@mcp.prompt()
def incident_summary(service: str) -> str:
    """Draft an incident summary for a service."""
    return f"Write a blameless incident summary for {service} using our on-call guide."

if __name__ == "__main__":
    mcp.run()  # speaks MCP over stdio
