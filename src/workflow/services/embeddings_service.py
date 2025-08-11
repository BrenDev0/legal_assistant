from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredExcelLoader,
    UnstructuredWordDocumentLoader
)
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import os
from typing import Optional, List, Dict
import uuid
import time
from langchain_core.documents import Document

class EmbeddingService:
    def __init__(self, embedding_model=None):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        
        self.embedding_model = embedding_model or OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        self.loader_mapping = {
            'application/pdf': PyPDFLoader,
            'text/plain': TextLoader,
            'text/csv': CSVLoader,
            'application/vnd.ms-excel': UnstructuredExcelLoader,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': UnstructuredExcelLoader,
            'application/msword': UnstructuredWordDocumentLoader,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': UnstructuredWordDocumentLoader
        }

    @staticmethod
    def get_collection_name(user_id: str, agent_id: str) -> str:
        """Generate standardized collection names."""
        return f"user_{user_id}_agent_{agent_id}"
    
    async def create_collection(self, user_id: str, agent_id: str) -> bool:
        collection_name = self.get_collection_name(user_id, agent_id)
        try:
            self.client.get_collection(collection_name)
            return False  
        except:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=3072,
                    distance=Distance.COSINE
                ),
            )
            return True

    async def delete_user_data(self, user_id: str) -> int: 
        deleted = 0
        collections = self.client.get_collections()
        prefix = f"user_{user_id}_agent_"
        
        for collection in collections.collections:
            if collection.name.startswith(prefix):
                self.client.delete_collection(collection.name)
                deleted += 1
        return deleted

    async def _load_document_from_url(
        self,
        s3_url: str,
        file_type: str,
        filename: str
    ) -> List[Dict]:
        loader_class = self.loader_mapping.get(file_type)
        if not loader_class:
            raise ValueError(f"Unsupported file type: {file_type}")

        loader = loader_class(s3_url)
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)

        return [{
            "text": chunk.page_content,
            "metadata": {
                **chunk.metadata,
                "original_filename": filename,
                "chunk_id": str(uuid.uuid4())
            }
        } for chunk in chunks]

    async def embed_uploaded_document(
        self,
        s3_url: str,
        file_type: str,
        filename: str,
        user_id: str,
        agent_id: str,
        custom_metadata: Optional[Dict] = None
    ) -> Dict:
        collection_name = self.get_collection_name(user_id, agent_id)
        await self.create_collection(user_id, agent_id)

        chunks = await self._load_document_from_url(s3_url, file_type, filename)

        texts = [chunk["text"] for chunk in chunks]
        embeddings = await self.embedding_model.aembed_documents(texts)

        points = []
        for chunk, embedding in zip(chunks, embeddings):
            metadata = {
                "user_id": user_id,
                "agent_id": agent_id,
                "upload_timestamp": int(time.time()),
                **chunk["metadata"]
            }

            if custom_metadata:
                metadata.update(custom_metadata)

            points.append({
                "id": str(uuid.uuid4()),
                "vector": embedding,
                "payload": {
                    "text": chunk["text"],
                    "metadata": metadata
                }
            })

        self.client.upsert(
            collection_name=collection_name,
            points=points
        )

        return {
            "status": "success",
            "chunks_processed": len(points),
            "collection": collection_name,
            "document_id": str(uuid.uuid4())
        }

    async def search_for_context(
        self,
        input: str,
        agent_id: str,
        user_id: str,
        tok_k: int = 4
    ) -> List[Document]:
        collection_name = self.get_collection_name(user_id=user_id, agent_id=agent_id)
        query_embedding = await self.embedding_model.aembed_query(input)

        search_results = self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=tok_k,
            with_payload=True
        )

        if not search_results:
            return None

        docs =  [
            Document(
                page_content=item.payload["text"]
            ) for item in search_results
        ]

        return  "\n\n".join([doc.page_content for doc in docs])


    def scroll(self, user_id: str, agent_id: str):
        results, _ = self.client.scroll(
            collection_name=f"user_{user_id}_agent_{agent_id}",
            limit=10,
            with_payload=True
        )

        for point in results:
            print(point.payload)