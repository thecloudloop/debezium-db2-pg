from confluent_kafka import Consumer
import psycopg2
import json
from datetime import datetime

# Initialise properties
bootstrap_servers_address = "host.docker.internal:9092"    # Change to your kafka server address
first_topic_name = "db2inst1.testdb"    # Change to your topic
consumer_group_id = "pgsync"

# Create Kafka config dictionary
kafkaConsumerConfig = {
    'bootstrap.servers': bootstrap_servers_address,
    'group.id': consumer_group_id,
    'auto.offset.reset': 'earliest'
}

# Initialise Consumer
consumer = Consumer(kafkaConsumerConfig)
consumer.subscribe([first_topic_name])
dbconn = psycopg2.connect(host="host.docker.internal", user="postgres", password="postgres", database="testdb", port=5432)
dbconn.set_session(autocommit=True)

# Loop through messages
try:
    dbcur = dbconn.cursor()
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
        if msg.key():
            print(f' Key: {msg.key().decode("utf-8")}, message: {msg.value() and msg.value().decode("utf-8") or None}')
            try:
               msgval = msg.value().decode("utf-8")
               msgval = json.loads( msgval )
            except:
               pass
            try:
               msgkey = msg.key().decode("utf-8")
               msgkey = json.loads( msgkey )
            except:
               pass
            payload = msgval.get("payload", {})
            meta_schema = msgval.get("schema", {}).get("fields", [])
            meta_before = []
            meta_after = []
            for x in meta_schema:
                if x.get("field") == "before":
                    meta_before = x.get("fields")
                elif x.get("field") == "after":
                    meta_after = x.get("fields")
            # print ("Value of meta {}".format(meta_schema))
            # print ("Value of meta before {}".format(meta_before))
            # print ("Value of meta after {}".format(meta_after))
            key = msgkey.get("payload", {})
            source = payload.get("source", {})
            schema = source and source.get("schema").lower() or None
            table = source and source.get("table").lower() or None
            opn = payload and payload.get("op") or None
            if not (source and schema and table):
                print ("Source {}, Schema {} or Table {} Info not found, Skipping to next event".format(source, schema, table))
                continue
            if opn in ["c", "i"]:
                sql = "insert into {}.{}".format(schema, table)
                collist = ""
                vallist = ""
                tuplelist = []
                for k, v in payload.get("after").items():
                    x = [ x for x in meta_after if x.get("field").lower() == k.lower() ]
                    # print ("Value of x {}".format(x))
                    if x and x[0].get("name") == "org.apache.kafka.connect.data.Date":
                        v = datetime.fromtimestamp(v * 24 * 60 * 60 )
                    if not collist:
                        collist = k
                        vallist = "%s"
                        tuplelist = [ v ]
                    else:
                        collist = collist + ', ' + k
                        vallist = vallist + ', %s'
                        tuplelist.append(v)
                dbcur.execute( sql + '(' + collist + ') values (' + vallist + ');', tuple(tuplelist) )
            elif opn in ["d"]:
                sql = "delete from {}.{}".format(schema, table)
                whereclause = ""
                tuplelist = []
                for k, v in key.items():
                    x = [ x for x in meta_before if x.get("field").lower() == k.lower() ]
                    if x and x[0].get("name") == "org.apache.kafka.connect.data.Date":
                        v = datetime.fromtimestamp(v * 24 * 60 * 60 )
                    if not whereclause:
                        whereclause = k + ' = %s'
                    else:
                        whereclause = whereclause + ' and ' + k + ' = %s'
                    tuplelist.append(v)
                dbcur.execute( sql + ' where ' + whereclause + ';', tuple(tuplelist) )
            elif opn in ["u"]:
                sql = "update {}.{}".format(schema, table)
                setclause = ""
                whereclause = ""
                tuplelist1 = []
                tuplelist2 = []
                for k, v in payload.get("after").items():
                    x = [ x for x in meta_after if x.get("field").lower() == k.lower() ]
                    if x and x[0].get("name") == "org.apache.kafka.connect.data.Date":
                        v = datetime.fromtimestamp(v * 24 * 60 * 60 )
                    if not setclause:
                        setclause = k + ' = %s'
                    else:
                        setclause = setclause + ', '+ k +' = %s'
                    tuplelist1.append(v)
                for k, v in key.items():
                    x = [ x for x in meta_before if x.get("field").lower() == k.lower() ]
                    if x and x[0].get("name") == "org.apache.kafka.connect.data.Date":
                        v = datetime.fromtimestamp(v * 24 * 60 * 60 )
                    if not whereclause:
                        whereclause = k +' = %s'
                    else:
                        whereclause = whereclause + ', ' + k + ' = %s'
                    tuplelist2.append(v)
                tuplelist = tuplelist1 + tuplelist2
                dbcur.execute( sql + ' set ' + setclause + ' where ' + whereclause + ';', tuple(tuplelist) )
        else:
            print(f' Key: None, message: {msg.value().decode("utf-8")}')
        print(f' Partition: {msg.partition()}, offset: {msg.offset()}')
except KeyboardInterrupt:
    dbconn.commit()
    dbconn.close()
    print("Stopped Consuming messages from Kafka")
finally:
    # Close consumer
    consumer.close()
