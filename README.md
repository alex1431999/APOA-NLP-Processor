# APOAX NLP Processor
## Setup
Make sure python 3.6 and virtualenv are installed and that the URL pointing to the common repository is replaced by your own URL.

Run the following:
```sh
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Files Required
Please add all these files to your folder with the missing parts filled in.
### google_cloud_NLP_private_key.json
```json
{
  "type": "service_account",
  "project_id": "",
  "private_key_id": "",
  "private_key": "",
  "client_email": "",
  "client_id": "",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": ""
}
```

### set_env.sh
```sh
source ./venv/bin/activate
export PYTHON_ENV="DEVELOPMENT" # DEVELOPMENT / PRODUCTION

# Mongo
# mongodb://localhost:27017
# mongodb+srv://admin:rofmEkKKWcmpuo4Q@final-year-project-lodcv.mongodb.net/test?retryWrites=true&w=majority&ssl_cert_reqs=CERT_NONE
export MONGO_CONNECTION_STRING="mongodb://localhost:27017"
export MONGO_DB_NAME="default_db"

# Neo4J
export NEO_CONNECTION_STRING="bolt://localhost:7687"
export NEO_USER="neo4j"
export NEO_PASSWORD="root"

# Celery
export BROKER_URL="amqp://guest:guest@localhost:5672"

# Secrets
export GOOGLE_APPLICATION_CREDENTIALS="" # The path to your credentials
```
