# defaults module

STREAMS_URL = "https://streams-api.aws-prod-streams-master-1.moralis.io"
SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 8080
QSIZE = 1024
ROW_LIMIT = 100
PAGE_LIMIT = 10000
REGION_CHOICES = ["us-east-1", "us-west-2", "eu-central-1", "ap-southeast-1"]
REGION = REGION_CHOICES[0]
ACTIVE = "active"
PAUSED = "paused"
ERROR = "error"
STATUS_CHOICES = [ACTIVE, PAUSED, ERROR]
