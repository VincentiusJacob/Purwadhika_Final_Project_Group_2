import os
from dotenv import load_dotenv
import time 
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_openai import OpenAIEmbeddings
from qdrant_client.http import models

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.getenv("OPENAI_API_KEY")
)

cutoff_ts = int(time.time()) - (30*60)

# Get collection
qdrant = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name="uploaded_cvs",
    url=os.getenv("QDRANT_ENDPOINT"),
    api_key=os.getenv("QDRANT_API_KEY")
)

client = qdrant.client  # QdrantClient

# client.create_payload_index(
#     collection_name="uploaded_cvs",
#     field_name="metadata.created",
#     field_schema=models.PayloadSchemaType.INTEGER
# )


# From collection, get points where metadata:time_created < time.now() - 30 minutes
_filter = models.Filter(
    must=[
        models.FieldCondition(
            key="metadata.created",
            range=models.Range(lt=cutoff_ts)
        )
    ]
)


points, _ = client.scroll(
    collection_name="uploaded_cvs",
    scroll_filter=_filter,
    limit=10000,
    with_payload=True,
    with_vectors=False
)

# Delete points from collection
_ids = []
for point in points:
    _ids.append(point.id)

qdrant.delete(
    ids=_ids
)

# Check remaining points
points, _ = client.scroll(
    collection_name="uploaded_cvs",
    # scroll_filter=_filter,
    limit=10000,
    with_payload=False,
    with_vectors=False
)

print(points)
# for point in points:
#     print(point.payload["metadata"]["created"])