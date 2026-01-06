from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .models import RecommendResponse
from .recommender import default_recommender

mcp = FastMCP("MoodMusic")


@mcp.tool()
def recommend_songs(mood_text: str, k: int = 5) -> dict:
    """Recommend songs for a free-form mood description.

    Args:
        mood_text: One or more sentences describing the user's mood.
        k: How many recommendations to return (1-20).

    Returns:
        JSON-serializable dict containing model name and results.
    """

    rec = default_recommender()
    hits = rec.recommend(mood_text, k=k)
    return RecommendResponse(model=rec.config.model_name, results=hits).model_dump()


def main() -> None:
    # Runs an MCP server over stdio.
    mcp.run()
