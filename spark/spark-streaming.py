from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import StructType, StructField, StringType, LongType, BooleanType
import requests

# Define the schema for posts and comments
post_schema = StructType([
    StructField("id", StringType(), True),
    StructField("title", StringType(), True),
    StructField("author", StringType(), True),
    StructField("selftext", StringType(), True),
    StructField("subreddit", StringType(), True),
    StructField("upvotes", LongType(), True),
    StructField("downvotes", LongType(), True),
    StructField("over_18", BooleanType(), True),
    StructField("timestamp", LongType(), True),
    StructField("permalink", StringType(), True),
])

comment_schema = StructType([
    StructField("id", StringType(), True),
    StructField("name", StringType(), True),
    StructField("author", StringType(), True),
    StructField("body", StringType(), True),
    StructField("subreddit", StringType(), True),
    StructField("upvotes", LongType(), True),
    StructField("downvotes", LongType(), True),
    StructField("over_18", BooleanType(), True),
    StructField("timestamp", LongType(), True),
    StructField("permalink", StringType(), True),
    StructField("post_id", StringType(), True),
])

# Initialize Spark session
spark = SparkSession.builder \
    .appName("RedditSentimentAnalysis") \
    .getOrCreate()

# Create DataStreamReader for Kafka
kafka_reader = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "reddit_posts,reddit_comments") \
    .option("startingOffsets", "earliest")

# Read data from Kafka
raw_df = kafka_reader.load()

# Extract and parse the JSON payload
posts_df = raw_df.filter(col("topic") == "reddit_posts") \
    .select(from_json(col("value").cast("string"), post_schema).alias("data")) \
    .select("data.*")

comments_df = raw_df.filter(col("topic") == "reddit_comments") \
    .select(from_json(col("value").cast("string"), comment_schema).alias("data")) \
    .select("data.*")

# Define a UDF to perform sentiment prediction by calling the FastAPI service
def predict_sentiment(post_title, post_body, comment_body):
    text = f"post title: {post_title} post: {post_body} comment: {comment_body}".lower()
    response = requests.post("http://172.18.0.10:8081/predict", json={"text": text})
    if response.status_code == 200:
        return response.json()["sentiment"]
    else:
        return "error"

predict_sentiment_udf = udf(predict_sentiment, StringType())

# Apply the UDF to the comments dataframe
comments_with_sentiment_df = comments_df.withColumn("sentiment", predict_sentiment_udf(col("post_title"), col("post_body"), col("comment_body")))

# Write the posts to the posts table
posts_df.writeStream \
    .format("org.apache.spark.sql.cassandra") \
    .option("keyspace", "reddit") \
    .option("table", "posts") \
    .option("checkpointLocation", "/tmp/checkpoint_posts") \
    .start()

# Write the comments with sentiment to the comments_with_sentiment table
comments_with_sentiment_df.writeStream \
    .format("org.apache.spark.sql.cassandra") \
    .option("keyspace", "reddit") \
    .option("table", "comments_with_sentiment") \
    .option("checkpointLocation", "/tmp/checkpoint_comments") \
    .start() \
    .awaitTermination()
