import threading
import praw
import yaml
import logging
import json
from kafka import KafkaProducer

logger = logging.getLogger('reddit_streamer')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class RedditStreamer:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.reddit = self.init_reddit(self.config['credentials']['reddit'])
        self.producer = self.init_kafka_producer(self.config['kafka'])
        self.subreddit_list = self.config['subreddits']['list']
        self.keywords = self.config['keywords']
        self.threads = []

    @staticmethod
    def load_config(config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            logger.info(f"Loaded config: {config}")
            return config

    @staticmethod
    def init_reddit(credentials):
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        for logger_name in ("praw", "prawcore"):
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)
            logger.addHandler(handler)
        return praw.Reddit(**credentials)

    @staticmethod
    def init_kafka_producer(kafka_config):
        return KafkaProducer(
            bootstrap_servers=kafka_config['bootstrap_servers'],
            value_serializer=lambda x: json.dumps(x, indent=4).encode('utf-8'),
            retries=5,
            request_timeout_ms=30000,
            retry_backoff_ms=5000
        )

    def stream_comments(self, subreddit_name):
        subreddit = self.reddit.subreddit(subreddit_name)
        for comment in subreddit.stream.comments(skip_existing=True):
            try:
                comment_json = {
                    "id": comment.id,
                    "name": comment.name,
                    "author": comment.author.name if comment.author else None,
                    "body": comment.body,
                    "subreddit": comment.subreddit.display_name,
                    "upvotes": comment.ups,
                    "downvotes": comment.downs,
                    "over_18": comment.over_18,
                    "timestamp": comment.created_utc,
                    "permalink": comment.permalink,
                    "post_id": comment.link_id.split('_')[1]
                }
                self.producer.send("reddit_comments", value=comment_json)
                logger.info(f"Streamed comment from subreddit '{subreddit_name}'",
                            extra={'comment_id': comment_json['id']})
            except Exception as e:
                logger.error(f"Error streaming comment from subreddit '{subreddit_name}'", exc_info=True)

    def stream_posts(self, subreddit_name):
        subreddit = self.reddit.subreddit(subreddit_name)
        for submission in subreddit.stream.submissions(skip_existing=True):
            try:
                if any(keyword in submission.title.lower() or keyword in submission.selftext.lower() for keyword in self.keywords):
                    post_json = {
                        "id": submission.id,
                        "title": submission.title,
                        "author": submission.author.name if submission.author else None,
                        "selftext": submission.selftext,
                        "subreddit": submission.subreddit.display_name,
                        "upvotes": submission.ups,
                        "downvotes": submission.downs,
                        "over_18": submission.over_18,
                        "timestamp": submission.created_utc,
                        "permalink": submission.permalink,
                    }
                    self.producer.send("reddit_posts", value=post_json)
                    logger.info(f"Streamed post from subreddit '{subreddit_name}'", extra={'post_id': post_json['id']})
            except Exception as e:
                logger.error(f"Error streaming post from subreddit '{subreddit_name}'", exc_info=True)

    def start_streaming_threads(self):
        for subreddit_name in self.subreddit_list:
            comment_thread = threading.Thread(target=self.stream_comments, args=(subreddit_name,))
            post_thread = threading.Thread(target=self.stream_posts, args=(subreddit_name,))
            comment_thread.start()
            post_thread.start()
            self.threads.append(comment_thread)
            self.threads.append(post_thread)
            logger.info(f"Started streaming comments and posts for subreddit '{subreddit_name}'")

        for thread in self.threads:
            thread.join()

if __name__ == "__main__":
    streamer = RedditStreamer("./config/config.yaml")
    streamer.start_streaming_threads()
