FROM bitnami/spark:latest

USER root

# Install necessary libraries
RUN pip install pyspark kafka-python requests

# Add Kafka and Cassandra connectors
ADD https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.2.1/spark-sql-kafka-0-10_2.12-3.2.1.jar /opt/bitnami/spark/jars/
ADD https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector_2.12/3.3.0/spark-cassandra-connector_2.12-3.3.0.jar /opt/bitnami/spark/jars/

# Set the working directory
WORKDIR /app

# Copy the Spark streaming script
COPY spark-streaming.py /app/

# Copy utility scripts if any
COPY utils /app/utils

# Set the entrypoint
ENTRYPOINT ["spark-submit", "/app/spark-streaming.py"]
