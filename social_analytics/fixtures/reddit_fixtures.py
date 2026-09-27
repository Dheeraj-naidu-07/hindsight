"""
Realistic raw API response fixtures for Reddit API (OAuth / JSON endpoints).
"""

REDDIT_USER_FIXTURE = {
    "kind": "t2",
    "data": {
        "id": "u_dev_789",
        "name": "DistributedDev",
        "created_utc": 1642240800.0,
        "link_karma": 14200,
        "comment_karma": 8900,
        "total_karma": 23100,
        "subreddit": {
            "title": "Distributed Systems & Memory Architectures",
            "public_description": "Building stateful agents and evaluating long-term memory.",
            "subscribers": 1450,
        },
    },
}

REDDIT_SUBMITTED_FIXTURE = {
    "kind": "Listing",
    "data": {
        "after": "t3_post_after_token",
        "dist": 4,
        "children": [
            {
                "kind": "t3",
                "data": {
                    "id": "rd_post_201",
                    "title": "We benchmarked semantic vector recall vs temporal knowledge graphs for agents - here are the results",
                    "subreddit": "MachineLearning",
                    "author": "DistributedDev",
                    "score": 340,
                    "upvote_ratio": 0.94,
                    "num_comments": 82,
                    "num_crossposts": 6,
                    "created_utc": 1788523200.0,  # ~2026-09-05T12:00:00Z
                    "is_self": True,
                    "permalink": "/r/MachineLearning/comments/rd_post_201/we_benchmarked/",
                    "over_18": False,
                    "total_awards_received": 2,
                    "view_count": None,  # Reddit does not expose public view counts on API
                },
            },
            {
                "kind": "t3",
                "data": {
                    "id": "rd_post_202",
                    "title": "Show: Open source CLI for synchronizing local agent memories in Rust",
                    "subreddit": "rust",
                    "author": "DistributedDev",
                    "score": 580,
                    "upvote_ratio": 0.97,
                    "num_comments": 114,
                    "num_crossposts": 12,
                    "created_utc": 1789128000.0,  # ~2026-09-12T12:00:00Z
                    "is_self": True,
                    "permalink": "/r/rust/comments/rd_post_202/show_open_source_cli/",
                    "over_18": False,
                    "total_awards_received": 4,
                    "view_count": None,
                },
            },
            {
                "kind": "t3",
                "data": {
                    "id": "rd_post_203",
                    "title": "Why cosine similarity alone fails when your agent needs to recall facts across 50 sessions",
                    "subreddit": "LocalLLaMA",
                    "author": "DistributedDev",
                    "score": 420,
                    "upvote_ratio": 0.91,
                    "num_comments": 95,
                    "num_crossposts": 8,
                    "created_utc": 1789732800.0,  # ~2026-09-19T12:00:00Z
                    "is_self": True,
                    "permalink": "/r/LocalLLaMA/comments/rd_post_203/why_cosine_similarity_fails/",
                    "over_18": False,
                    "total_awards_received": 1,
                    "view_count": None,
                },
            },
            {
                "kind": "t3",
                "data": {
                    "id": "rd_post_204",
                    "title": "Ask: What strategies do you use for compacting conversational transcripts without loss of entities?",
                    "subreddit": "LangChain",
                    "author": "DistributedDev",
                    "score": 115,
                    "upvote_ratio": 0.86,
                    "num_comments": 47,
                    "num_crossposts": 2,
                    "created_utc": 1790337600.0,  # ~2026-09-26T12:00:00Z
                    "is_self": True,
                    "permalink": "/r/LangChain/comments/rd_post_204/ask_what_strategies_do_you_use/",
                    "over_18": False,
                    "total_awards_received": 0,
                    "view_count": None,
                },
            },
        ],
    },
}

REDDIT_AUDIENCE_FIXTURE = {
    "subscribers_start": 1390,
    "subscribers_end": 1450,
}
