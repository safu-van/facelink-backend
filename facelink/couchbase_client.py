from django.conf import settings
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator

config = settings.COUCHBASE_CONFIG

cluster = Cluster(
    config["HOST"],
    ClusterOptions(PasswordAuthenticator(config["USERNAME"], config["PASSWORD"])),
)

bucket = cluster.bucket(config["BUCKET"])
collection = bucket.default_collection()