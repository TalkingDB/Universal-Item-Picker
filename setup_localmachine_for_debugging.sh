HOST="com.smarter.codes"
GoogleCloudInstanceID="develop-special-instructions"

rm -rf backup_of_databases
mkdir backup_of_databases

mongodump -h $HOST --out backup_of_databases/remote_mongodb/
mongodump -h localhost --out backup_of_databases/local_mongodb/

mongo noisy_NER --eval "db.dropDatabase()"

mongorestore backup_of_databases/remote_mongodb/noisy_NER/ -d noisy_NER

sudo /var/lib/neo4j/bin/neo4j stop
sudo rm -rf /var/lib/neo4j/data/graph.db
gcloud compute copy-files anil.gautam@$GoogleCloudInstanceID:/var/lib/neo4j/data/graph.db backup_of_databases/ --zone europe-west1-c
sudo mv -r backup_of_databases/graph.db /var/lib/neo4j/data/
sudo /var/lib/neo4j/bin/neo4j start

python ../CommandNet_Processor/src/main.py gml 5012 train_UIP_from_learnt_answers


echo ""
echo "Please copy backup_of_databases/local_mongodb/ to a safer place. Otherwise you may use crucial training data copied from backup"
