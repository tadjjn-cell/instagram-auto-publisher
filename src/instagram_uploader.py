import logging
import time

import httpx

logger = logging.getLogger(__name__)

GRAPH_ROOT = "https://graph.facebook.com/v19.0"


def upload_reel(access_token: str, ig_user_id: str, video_url: str, caption: str) -> str:
    """
    Publish a public video URL as an Instagram Reel via the Content Publishing API.
    Instagram fetches the video itself from video_url (no direct byte upload) --
    the caller is responsible for hosting it at a temporary public URL first.
    Returns the published media id.
    """
    with httpx.Client(timeout=60) as client:
        create_resp = client.post(
            f"{GRAPH_ROOT}/{ig_user_id}/media",
            data={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "access_token": access_token,
            },
        )
        create_data = create_resp.json()
        if "id" not in create_data:
            raise Exception(f"Instagram media container creation failed: {create_data}")
        creation_id = create_data["id"]

        status = None
        for _ in range(30):  # up to ~5 minutes
            time.sleep(10)
            status_resp = client.get(
                f"{GRAPH_ROOT}/{creation_id}",
                params={"fields": "status_code,status", "access_token": access_token},
            )
            status_data = status_resp.json()
            status = status_data.get("status_code")
            if status == "FINISHED":
                break
            if status == "ERROR":
                raise Exception(f"Instagram failed to process the video: {status_data}")

        if status != "FINISHED":
            raise Exception(f"Instagram video processing timed out (last status: {status})")

        publish_resp = client.post(
            f"{GRAPH_ROOT}/{ig_user_id}/media_publish",
            data={"creation_id": creation_id, "access_token": access_token},
        )
        publish_data = publish_resp.json()
        if "id" not in publish_data:
            raise Exception(f"Instagram publish failed: {publish_data}")

        return publish_data["id"]
