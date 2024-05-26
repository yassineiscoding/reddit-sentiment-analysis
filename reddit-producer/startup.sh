#!/bin/bash

# Wait for Zookeeper
until nc -z zookeeper 2181; do
  echo "Waiting for Zookeeper..."
  sleep 5
done

# Wait for Kafka
until nc -z kafka 9092; do
  echo "Waiting for Kafka..."
  sleep 5
done

# Wait for Cassandra
until nc -z cassandra 9042; do
  echo "Waiting for Cassandra..."
  sleep 5
done

# Start the reddit-producer application
exec python reddit-producer.py
