FROM grafana/grafana-oss:9.2.6

COPY . .

RUN /bin/bash -c 'grafana-cli plugins install hadesarchitect-cassandra-datasource'

EXPOSE 3000