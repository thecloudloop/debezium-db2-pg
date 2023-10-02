ARG DEBEZIUM_VERSION
ARG JMX_AGENT_VERSION
FROM quay.io/debezium/connect:$DEBEZIUM_VERSION
ENV KAFKA_CONNECT_JDBC_DIR=$KAFKA_CONNECT_PLUGINS_DIR/kafka-connect-jdbc

USER root

# These should point to the driver version to be used
ENV MAVEN_DEP_DESTINATION=$KAFKA_HOME/libs \
    ORACLE_JDBC_REPO="com/oracle/database/jdbc" \
    ORACLE_JDBC_GROUP="ojdbc8" \
    ORACLE_JDBC_VERSION="21.6.0.0" \
    ORACLE_JDBC_MD5=312e6f4ec9932bbf74a4461669970c4b

RUN docker-maven-download central "$ORACLE_JDBC_REPO" "$ORACLE_JDBC_GROUP" "$ORACLE_JDBC_VERSION" "$ORACLE_JDBC_MD5"

RUN microdnf -y install libaio curl unzip python3-devel && microdnf clean all && pip3 install psycopg2-binary confluent_kafka

USER kafka

COPY confluentinc-kafka-connect-jdbc-10.7.4.zip $KAFKA_CONNECT_PLUGINS_DIR/
RUN cd $KAFKA_CONNECT_PLUGINS_DIR && unzip confluentinc-kafka-connect-jdbc-10.7.4.zip -d . && cd -

RUN curl https://repo1.maven.org/maven2/com/ibm/db2/jcc/11.5.0.0/jcc-11.5.0.0.jar --output /kafka/connect/debezium-connector-db2/jcc-11.5.0.0.jar
RUN cd $KAFKA_CONNECT_PLUGINS_DIR && curl https://repo1.maven.org/maven2/io/debezium/debezium-connector-jdbc/2.3.2.Final/debezium-connector-jdbc-2.3.2.Final-plugin.tar.gz --output debezium-connector-jdbc-2.3.2.Final-plugin.tar.gz && tar -xvzf debezium-connector-jdbc-2.3.2.Final-plugin.tar.gz && rm -f debezium-connector-jdbc-2.3.2.Final-plugin.tar.gz && cd -
RUN cd /kafka/libs && curl -o jcustenborder-kafka-connect-transform-common-0.1.0.58.zip https://d1i4a15mxbxib1.cloudfront.net/api/plugins/jcustenborder/kafka-connect-transform-common/versions/0.1.0.58/jcustenborder-kafka-connect-transform-common-0.1.0.58.zip && unzip jcustenborder-kafka-connect-transform-common-0.1.0.58.zip -d . && cp -f jcustenborder-kafka-connect-transform-common-0.1.0.58/lib/*jar . && rm jcustenborder-kafka-connect-transform-common-0.1.0.58.zip &&  cd -
RUN cd /kafka/libs && curl -o guava-32.1.2-jre.jar https://repo1.maven.org/maven2/com/google/guava/guava/32.1.2-jre/guava-32.1.2-jre.jar && cd -
RUN mkdir /kafka/etc && cd /kafka/etc && curl -o jmx_prometheus_javaagent.jar https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.20.0/jmx_prometheus_javaagent-0.20.0.jar && cd -

COPY config.yml /kafka/etc/config.yml
COPY kafka_consumer.py /kafka
