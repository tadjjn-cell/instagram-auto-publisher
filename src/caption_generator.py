import json
import logging

from src.config import get_groq_client, call_groq_with_retry

logger = logging.getLogger(__name__)


async def generate_instagram_caption(topic: str, trending_queries: list[str], config: dict) -> dict:
    """Call Groq (free tier) to turn a topic + trend signal into an Instagram Reels caption."""
    client = get_groq_client(config)
    model = config.get("ai", {}).get("text_model", "openai/gpt-oss-120b")
    trending_str = ", ".join(trending_queries) if trending_queries else "(none found)"

    response_text = await call_groq_with_retry(
        client,
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an Instagram growth expert who writes Reels captions optimized "
                    "for reach and saves/shares. Return ONLY valid JSON."
                ),
            },
            {
                "role": "user",
                "content": f"""Write an Instagram Reels caption for a video about: "{topic}"

Currently trending/rising search queries around this topic (last 7 days): {trending_str}

Rules:
- caption: 2-4 short lines. First line is the hook (shown before "...more"). Can include a short CTA (save/share/follow). Emojis allowed but not excessive.
- hashtags: a list of 8-15 hashtags (no # symbol, code will add it): mix a couple of broad reach tags with specific/trending niche tags. Prioritize wording from the trending queries when it fits.

Return JSON with exactly these keys: caption, hashtags""",
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
        max_tokens=1024,
        reasoning_effort="low",
    )

    data = json.loads(response_text)
    return {
        "caption": str(data["caption"])[:2200],
        "hashtags": [str(h) for h in data.get("hashtags", [])][:15],
    }
