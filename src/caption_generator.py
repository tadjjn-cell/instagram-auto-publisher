import json
import logging

from src.config import get_groq_client, call_groq_with_retry

logger = logging.getLogger(__name__)


async def generate_instagram_caption(topic: str, trending_queries: list[str], config: dict) -> dict:
    """Call Groq (free tier) to turn a topic + trend signal into an Instagram Reels caption."""
    client = get_groq_client(config)
    model = config.get("ai", {}).get("text_model", "openai/gpt-oss-120b")
    trending_str = ", ".join(trending_queries) if trending_queries else "(none found)"

    product = config.get("product", {})
    if product.get("enabled") and product.get("name"):
        product_rules = f"""
This account sells a digital product: "{product['name']}" -- {product.get('description', '')}
Structure the caption as VALUE FIRST, SELL SECOND:
- Line 1: a hook about the video's topic (the video itself is the value, not an ad).
- Lines 2-3: one useful, specific takeaway related to the topic.
- Then ONE short, natural bridge to the product (what problem it solves for the viewer) and this exact call-to-action on its own line: "{product.get('cta', 'Link in bio')}".
Never make income/health/result guarantees, never use fake urgency or fake scarcity, never claim testimonials that were not provided. Links are not clickable in Instagram captions, so do not write a URL."""
    else:
        product_rules = ""

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
- caption: 2-5 short lines. First line is the hook (shown before "...more"). Emojis allowed but not excessive.{product_rules}
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
