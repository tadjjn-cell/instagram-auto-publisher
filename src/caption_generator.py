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
    items = product.get("items", [])
    if product.get("enabled") and items:
        catalog = "\n".join(f"- {i['name']}: {i.get('description', '')}" for i in items)
        product_rules = f"""
This account sells digital printables at "{product.get('store', 'our store')}":
{catalog}
Structure the caption as VALUE FIRST, SELL SECOND:
- Line 1: a hook about the video's topic (the video itself is the value, not an ad).
- Lines 2-3: one useful, specific takeaway related to the topic.
- Then, ONLY IF one product above clearly matches the topic, one short natural bridge naming that ONE product and the everyday problem it helps with, followed by this exact call-to-action on its own line: "{product.get('cta', 'Link in bio')}". If no product clearly matches, skip the product mention entirely.
Hard rules: these are printable organizers, NOT medical products or advice. Never claim to treat, cure, manage, improve or prevent any medical or mental-health condition, never promise results or income, no before/after claims, no fake urgency or scarcity, no invented testimonials. Links are not clickable in Instagram captions, so do not write a URL."""
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
