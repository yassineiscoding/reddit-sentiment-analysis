CREATE KEYSPACE IF NOT EXISTS reddit WITH REPLICATION = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

CREATE TABLE IF NOT EXISTS reddit.posts (
    id TEXT PRIMARY KEY,
    title TEXT,
    author TEXT,
    selftext TEXT,
    subreddit TEXT,
    upvotes BIGINT,
    downvotes BIGINT,
    over_18 BOOLEAN,
    timestamp BIGINT,
    permalink TEXT
);

CREATE TABLE IF NOT EXISTS reddit.comments_with_sentiment (
    id TEXT PRIMARY KEY,
    name TEXT,
    author TEXT,
    body TEXT,
    subreddit TEXT,
    upvotes BIGINT,
    downvotes BIGINT,
    over_18 BOOLEAN,
    timestamp BIGINT,
    permalink TEXT,
    post_id TEXT,
    sentiment TEXT
);
