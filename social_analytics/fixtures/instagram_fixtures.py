"""
Realistic raw API response fixtures for Instagram Graph API.
"""

INSTAGRAM_USER_FIXTURE = {
    "id": "17841405822384912",
    "username": "tech_architect_daily",
    "name": "Alex Vance | Tech Architect",
    "biography": "Distributed systems, Python, AI agents. Building the future of autonomous workflows.",
    "followers_count": 18400,
    "follows_count": 312,
    "media_count": 142,
    "profile_picture_url": "https://instagram.example.com/profiles/tech_architect.jpg",
}

INSTAGRAM_MEDIA_FIXTURE = {
    "data": [
        {
            "id": "ig_media_101",
            "caption": "How we designed a biomimetic agent memory architecture in Python. Swipe to see the architecture diagram! 🧠 #systemdesign #ai",
            "media_type": "CAROUSEL_ALBUM",
            "media_product_type": "FEED",
            "timestamp": "2026-09-04T12:00:00+0000",
            "permalink": "https://instagram.com/p/Cxyz101/",
            "like_count": 640,
            "comments_count": 52,
            "insights": {
                "data": [
                    {"name": "impressions", "values": [{"value": 14200}]},
                    {"name": "reach", "values": [{"value": 11500}]},
                    {"name": "saved", "values": [{"value": 280}]},
                    {"name": "shares", "values": [{"value": 94}]},
                ]
            },
        },
        {
            "id": "ig_media_102",
            "caption": "3 reasons why your LLM agent keeps forgetting user preferences. #ai #agents #reels",
            "media_type": "VIDEO",
            "media_product_type": "REELS",
            "timestamp": "2026-09-11T17:15:00+0000",
            "permalink": "https://instagram.com/reel/Cxyz102/",
            "like_count": 1450,
            "comments_count": 118,
            "insights": {
                "data": [
                    {"name": "impressions", "values": [{"value": 31000}]},
                    {"name": "reach", "values": [{"value": 24200}]},
                    {"name": "saved", "values": [{"value": 410}]},
                    {"name": "shares", "values": [{"value": 320}]},
                    {"name": "plays", "values": [{"value": 27800}]},
                ]
            },
        },
        {
            "id": "ig_media_103",
            "caption": "A quick visual cheat sheet for RAG vs Long-Context LLMs. Save for later reference! 📌",
            "media_type": "IMAGE",
            "media_product_type": "FEED",
            "timestamp": "2026-09-18T14:30:00+0000",
            "permalink": "https://instagram.com/p/Cxyz103/",
            "like_count": 480,
            "comments_count": 31,
            "insights": {
                "data": [
                    {"name": "impressions", "values": [{"value": 9800}]},
                    {"name": "reach", "values": [{"value": 8100}]},
                    {"name": "saved", "values": [{"value": 340}]},
                    {"name": "shares", "values": [{"value": 62}]},
                ]
            },
        },
        {
            "id": "ig_media_104",
            "caption": "Behind the scenes of deploying a Rust-based CLI for memory sync! 🦀 #rust #developer",
            "media_type": "VIDEO",
            "media_product_type": "REELS",
            "timestamp": "2026-09-24T18:45:00+0000",
            "permalink": "https://instagram.com/reel/Cxyz104/",
            "like_count": 1820,
            "comments_count": 145,
            "insights": {
                "data": [
                    {"name": "impressions", "values": [{"value": 39500}]},
                    {"name": "reach", "values": [{"value": 31200}]},
                    {"name": "saved", "values": [{"value": 520}]},
                    {"name": "shares", "values": [{"value": 440}]},
                    {"name": "plays", "values": [{"value": 35400}]},
                ]
            },
        },
    ],
    "paging": {
        "cursors": {
            "after": "cursor_token_abc_123",
        }
    },
}

INSTAGRAM_AUDIENCE_FIXTURE = {
    "followers_start": 17850,
    "followers_end": 18400,
    "total_reach": 75000,
    "total_impressions": 94500,
}
