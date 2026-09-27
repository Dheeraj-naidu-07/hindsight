"""
Realistic raw API response fixtures for YouTube Data API v3 and Analytics API.
"""

YOUTUBE_CHANNEL_FIXTURE = {
    "kind": "youtube#channelListResponse",
    "etag": "etag_channel_test_123",
    "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
    "items": [
        {
            "kind": "youtube#channel",
            "etag": "item_etag_123",
            "id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
            "snippet": {
                "title": "Data Engineering Insights",
                "description": "Deep dives into distributed systems, AI memory, and streaming data.",
                "customUrl": "@dataenginsights",
                "publishedAt": "2023-01-15T10:00:00Z",
                "country": "US",
            },
            "statistics": {
                "viewCount": "482000",
                "subscriberCount": "24500",
                "hiddenSubscriberCount": False,
                "videoCount": "48",
            },
        }
    ],
}

YOUTUBE_VIDEOS_FIXTURE = {
    "kind": "youtube#videoListResponse",
    "etag": "etag_video_list_456",
    "items": [
        {
            "kind": "youtube#video",
            "id": "yt_vid_001",
            "snippet": {
                "publishedAt": "2026-09-02T14:00:00Z",
                "channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                "title": "Architecting Scalable Vector Databases for Agentic Memory",
                "description": "In this video we explore how agentic systems retain and retrieve memory.",
                "tags": ["vector-db", "ai", "agents", "memory"],
                "categoryId": "28",
            },
            "contentDetails": {
                "duration": "PT14M35S",
                "dimension": "2d",
                "definition": "hd",
                "caption": "true",
            },
            "statistics": {
                "viewCount": "12500",
                "likeCount": "890",
                "commentCount": "142",
            },
            # Preserved YouTube Analytics API extension
            "analytics": {
                "estimatedMinutesWatched": 4820.0,
                "averageViewDurationSeconds": 231.5,
                "subscribersGained": 85,
                "shares": 95,
                "impressions": 115000,
                "impressionClickThroughRate": 0.1087,
            },
        },
        {
            "kind": "youtube#video",
            "id": "yt_vid_002",
            "snippet": {
                "publishedAt": "2026-09-08T16:30:00Z",
                "channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                "title": "Why Pure RAG Fails for Autonomous Agents #shorts",
                "description": "Quick 45s breakdown on why semantic search alone cannot solve temporal memory.",
                "tags": ["rag", "ai", "shorts"],
                "categoryId": "28",
            },
            "contentDetails": {
                "duration": "PT48S",
                "dimension": "2d",
                "definition": "hd",
            },
            "statistics": {
                "viewCount": "45200",
                "likeCount": "3200",
                "commentCount": "310",
            },
            "analytics": {
                "estimatedMinutesWatched": 602.0,
                "averageViewDurationSeconds": 40.0,
                "subscribersGained": 230,
                "shares": 480,
                "impressions": 195000,
                "impressionClickThroughRate": 0.2318,
            },
        },
        {
            "kind": "youtube#video",
            "id": "yt_vid_003",
            "snippet": {
                "publishedAt": "2026-09-15T11:00:00Z",
                "channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                "title": "Comparing Graphiti vs Hindsight for Knowledge Synthesis",
                "description": "Benchmark comparison of modern agentic memory tools.",
                "tags": ["benchmarks", "ai", "memory"],
                "categoryId": "28",
            },
            "contentDetails": {
                "duration": "PT18M12S",
                "dimension": "2d",
                "definition": "hd",
            },
            "statistics": {
                "viewCount": "8400",
                "likeCount": "510",
                "commentCount": "88",
            },
            "analytics": {
                "estimatedMinutesWatched": 3100.0,
                "averageViewDurationSeconds": 221.4,
                "subscribersGained": 42,
                "shares": 62,
                "impressions": 82000,
                "impressionClickThroughRate": 0.1024,
            },
        },
        {
            "kind": "youtube#video",
            "id": "yt_vid_004",
            "snippet": {
                "publishedAt": "2026-09-22T18:00:00Z",
                "channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                "title": "Stop Using Plain Cosine Similarity #shorts",
                "description": "How BM25 + Cross-encoders change retrieval quality.",
                "tags": ["search", "embeddings", "shorts"],
                "categoryId": "28",
            },
            "contentDetails": {
                "duration": "PT55S",
                "dimension": "2d",
                "definition": "hd",
            },
            "statistics": {
                "viewCount": "38900",
                "likeCount": "2400",
                "commentCount": "215",
            },
            "analytics": {
                "estimatedMinutesWatched": 518.0,
                "averageViewDurationSeconds": 42.1,
                "subscribersGained": 180,
                "shares": 340,
                "impressions": 162000,
                "impressionClickThroughRate": 0.2401,
            },
        },
    ],
}

YOUTUBE_AUDIENCE_FIXTURE = {
    "subscribersStart": 23963,
    "subscribersEnd": 24500,
    "subscribersGainedTotal": 650,
    "subscribersLostTotal": 113,
    "totalImpressions": 554000,
}
