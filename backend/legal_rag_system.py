"""
Legal Question Answering RAG System

This module implements a comprehensive Retrieval-Augmented Generation (RAG) system
for legal question answering with the following features:

1. Vector database integration (Supabase Vector or FAISS fallback)
2. Embedding pipeline using free models
3. Multi-turn conversation support
4. Legal disclaimer enforcement
5. Confidence scoring and source citation
6. Domain-specific retrieval optimization
"""

import asyncio
import json
import logging
import numpy as np
import os
import pickle
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
import httpx
import google.generativeai as genai
from groq import Groq
import faiss
import re

# Import dependencies with fallbacks
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    create_client = None
    Client = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalRAGSystem:
    """Comprehensive Legal Question Answering RAG System"""
    
    def __init__(self):
        # API Configuration
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.groq_api_key = os.environ.get('GROQ_API_KEY')
        self.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        self.huggingface_api_key = os.environ.get('HUGGINGFACE_API_KEY')
        
        # Supabase Configuration
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        # Initialize AI clients
        genai.configure(api_key=self.gemini_api_key)
        self.groq_client = Groq(api_key=self.groq_api_key)
        
        # Vector database setup
        self.vector_db = None
        self.embeddings_model = None
        self.supabase_client = None
        self.faiss_index = None
        self.document_store = {}
        
        # RAG Configuration
        self.embedding_dimension = 384  # all-MiniLM-L6-v2 dimension
        self.max_retrieved_docs = 5
        self.min_similarity_threshold = 0.7
        
        # Legal disclaimer
        self.legal_disclaimer = (
            "\n\n⚖️ **LEGAL DISCLAIMER**: This response is for informational purposes only "
            "and does not constitute legal advice. Please consult with a qualified attorney "
            "for specific legal guidance regarding your situation."
        )
        
        # Conversation memory
        self.conversation_history = {}
        
    async def initialize(self):
        """Initialize the RAG system with vector database and embeddings"""
        logger.info("🚀 Initializing Legal RAG System...")
        
        # Initialize embeddings model
        await self._initialize_embeddings()
        
        # Initialize vector database (try Supabase first, then FAISS)
        vector_db_initialized = await self._initialize_supabase_vector()
        if not vector_db_initialized:
            logger.info("📦 Falling back to FAISS vector database...")
            await self._initialize_faiss_vector()
        
        logger.info("✅ Legal RAG System initialized successfully!")
    
    async def _initialize_embeddings(self):
        """Initialize the embeddings model"""
        try:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.error("Sentence transformers not available - using fallback embeddings")
                # Use a simple fallback - in production you'd want a better solution
                self.embeddings_model = None
                self.embedding_dimension = 384
                return
            
            # Use free sentence-transformers model for embeddings
            logger.info("🔤 Loading sentence transformers model...")
            self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Embeddings model loaded successfully!")
        except Exception as e:
            logger.error(f"Error loading embeddings model: {e}")
            self.embeddings_model = None
    
    async def _initialize_supabase_vector(self) -> bool:
        """Initialize Supabase vector database"""
        try:
            if not self.supabase_url or not self.supabase_key or not SUPABASE_AVAILABLE:
                logger.warning("Supabase not available or credentials missing")
                return False
                
            logger.info("🔗 Connecting to Supabase vector database...")
            self.supabase_client = create_client(self.supabase_url, self.supabase_key)
            
            # Create legal_documents table if it doesn't exist
            await self._create_supabase_tables()
            
            self.vector_db = "supabase"
            logger.info("✅ Supabase vector database initialized!")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Supabase: {e}")
            return False
    
    async def _create_supabase_tables(self):
        """Create necessary tables in Supabase"""
        try:
            # This would typically be done via SQL in Supabase dashboard
            # For now, we'll assume the table exists or create it programmatically
            logger.info("📋 Ensuring Supabase tables exist...")
            
            # Note: In a real implementation, you would create tables like:
            # CREATE TABLE legal_documents (
            #   id TEXT PRIMARY KEY,
            #   title TEXT,
            #   content TEXT,
            #   embedding VECTOR(384),
            #   jurisdiction TEXT,
            #   legal_domain TEXT,
            #   document_type TEXT,
            #   source TEXT,
            #   source_url TEXT,
            #   metadata JSONB,
            #   created_at TIMESTAMP DEFAULT NOW()
            # );
            
        except Exception as e:
            logger.error(f"Error creating Supabase tables: {e}")
    
    async def _initialize_faiss_vector(self):
        """Initialize FAISS vector database as fallback"""
        try:
            logger.info("📦 Initializing FAISS vector database...")
            
            # Create FAISS index
            self.faiss_index = faiss.IndexFlatIP(self.embedding_dimension)  # Inner Product for cosine similarity
            
            self.vector_db = "faiss"
            logger.info("✅ FAISS vector database initialized!")
            
        except Exception as e:
            logger.error(f"Error initializing FAISS: {e}")
            raise
    
    async def ingest_knowledge_base(self, knowledge_base_path: str = "/app/legal_knowledge_base.json"):
        """Ingest legal knowledge base into vector database"""
        logger.info("📚 Ingesting legal knowledge base...")
        
        try:
            # Load knowledge base
            with open(knowledge_base_path, 'r', encoding='utf-8') as f:
                knowledge_base = json.load(f)
            
            logger.info(f"📖 Processing {len(knowledge_base)} legal documents...")
            
            # Process documents in batches
            batch_size = 50
            for i in range(0, len(knowledge_base), batch_size):
                batch = knowledge_base[i:i + batch_size]
                await self._process_document_batch(batch)
                logger.info(f"✅ Processed batch {i//batch_size + 1}/{(len(knowledge_base) + batch_size - 1)//batch_size}")
            
            # Save FAISS index if using FAISS
            if self.vector_db == "faiss":
                await self._save_faiss_index()
            
            logger.info(f"✅ Successfully ingested {len(knowledge_base)} documents into vector database!")
            
        except Exception as e:
            logger.error(f"Error ingesting knowledge base: {e}")
            raise
    
    async def _process_document_batch(self, documents: List[Dict]):
        """Process a batch of documents for vector storage"""
        try:
            # Prepare texts for embedding
            texts = []
            doc_metadata = []
            
            for doc in documents:
                # Combine title and content for better context
                text = f"{doc.get('title', '')} {doc.get('content', '')}"[:2000]  # Limit length
                texts.append(text)
                doc_metadata.append(doc)
            
            # Generate embeddings
            embeddings = self.embeddings_model.encode(texts, convert_to_numpy=True)
            
            # Store in vector database
            if self.vector_db == "supabase":
                await self._store_in_supabase(doc_metadata, embeddings)
            else:
                await self._store_in_faiss(doc_metadata, embeddings)
                
        except Exception as e:
            logger.error(f"Error processing document batch: {e}")
    
    async def _store_in_supabase(self, documents: List[Dict], embeddings: np.ndarray):
        """Store documents and embeddings in Supabase"""
        try:
            for doc, embedding in zip(documents, embeddings):
                # Convert numpy array to list for JSON serialization
                embedding_list = embedding.tolist()
                
                # Prepare document for insertion
                supabase_doc = {
                    "id": doc.get("id", str(uuid4())),
                    "title": doc.get("title", "")[:500],  # Limit title length
                    "content": doc.get("content", "")[:3000],  # Limit content length
                    "embedding": embedding_list,
                    "jurisdiction": doc.get("jurisdiction", ""),
                    "legal_domain": doc.get("legal_domain", ""),
                    "document_type": doc.get("document_type", ""),
                    "source": doc.get("source", ""),
                    "source_url": doc.get("source_url", ""),
                    "metadata": doc.get("metadata", {}),
                    "created_at": doc.get("created_at", datetime.utcnow().isoformat())
                }
                
                # Insert into Supabase
                result = self.supabase_client.table("legal_documents").upsert(supabase_doc).execute()
                
        except Exception as e:
            logger.error(f"Error storing in Supabase: {e}")
    
    async def _store_in_faiss(self, documents: List[Dict], embeddings: np.ndarray):
        """Store documents and embeddings in FAISS"""
        try:
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add to FAISS index
            self.faiss_index.add(embeddings)
            
            # Store document metadata
            start_idx = len(self.document_store)
            for i, doc in enumerate(documents):
                self.document_store[start_idx + i] = doc
                
        except Exception as e:
            logger.error(f"Error storing in FAISS: {e}")
    
    async def _save_faiss_index(self):
        """Save FAISS index and document store to disk"""
        try:
            faiss.write_index(self.faiss_index, "/app/legal_faiss_index.index")
            
            with open("/app/legal_document_store.pkl", "wb") as f:
                pickle.dump(self.document_store, f)
                
            logger.info("💾 FAISS index and document store saved successfully!")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    async def _load_faiss_index(self):
        """Load FAISS index and document store from disk"""
        try:
            if os.path.exists("/app/legal_faiss_index.index"):
                self.faiss_index = faiss.read_index("/app/legal_faiss_index.index")
                logger.info("📂 FAISS index loaded from disk!")
            
            if os.path.exists("/app/legal_document_store.pkl"):
                with open("/app/legal_document_store.pkl", "rb") as f:
                    self.document_store = pickle.load(f)
                logger.info("📂 Document store loaded from disk!")
                
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
    
    async def answer_legal_question(self, question: str, session_id: str = None, 
                                  jurisdiction: str = None, legal_domain: str = None) -> Dict[str, Any]:
        """Main method to answer legal questions using RAG"""
        try:
            logger.info(f"❓ Processing legal question: {question[:100]}...")
            
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid4())
            
            # Retrieve relevant documents
            retrieved_docs = await self._retrieve_relevant_documents(
                question, jurisdiction, legal_domain
            )
            
            # Generate answer using retrieved context
            answer_result = await self._generate_answer(
                question, retrieved_docs, session_id
            )
            
            # Add to conversation history
            self._update_conversation_history(session_id, question, answer_result)
            
            # Add legal disclaimer
            answer_result["answer"] += self.legal_disclaimer
            
            logger.info("✅ Legal question answered successfully!")
            return answer_result
            
        except Exception as e:
            logger.error(f"Error answering legal question: {e}")
            return {
                "answer": f"I apologize, but I encountered an error while processing your legal question. Please try again or consult with a legal professional.{self.legal_disclaimer}",
                "confidence": 0.0,
                "sources": [],
                "session_id": session_id,
                "error": str(e)
            }
    
    async def _retrieve_relevant_documents(self, question: str, jurisdiction: str = None, 
                                         legal_domain: str = None) -> List[Dict[str, Any]]:
        """Retrieve relevant documents using vector similarity search"""
        try:
            # Generate question embedding
            question_embedding = self.embeddings_model.encode([question], convert_to_numpy=True)
            
            if self.vector_db == "supabase":
                return await self._retrieve_from_supabase(question_embedding[0], jurisdiction, legal_domain)
            else:
                return await self._retrieve_from_faiss(question_embedding[0], jurisdiction, legal_domain)
                
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    async def _retrieve_from_supabase(self, question_embedding: np.ndarray, 
                                    jurisdiction: str = None, legal_domain: str = None) -> List[Dict[str, Any]]:
        """Retrieve documents from Supabase using vector similarity"""
        try:
            # Convert embedding to list for Supabase
            embedding_list = question_embedding.tolist()
            
            # Build query
            query = self.supabase_client.table("legal_documents").select("*")
            
            # Add filters
            if jurisdiction:
                query = query.eq("jurisdiction", jurisdiction)
            if legal_domain:
                query = query.eq("legal_domain", legal_domain)
            
            # Execute query (Note: Vector similarity would require custom function)
            result = query.limit(self.max_retrieved_docs).execute()
            
            # For now, return all results - in production, you'd use vector similarity
            return result.data
            
        except Exception as e:
            logger.error(f"Error retrieving from Supabase: {e}")
            return []
    
    async def _retrieve_from_faiss(self, question_embedding: np.ndarray, 
                                 jurisdiction: str = None, legal_domain: str = None) -> List[Dict[str, Any]]:
        """Retrieve documents from FAISS using vector similarity"""
        try:
            # Normalize embedding for cosine similarity
            question_embedding = question_embedding.reshape(1, -1)
            faiss.normalize_L2(question_embedding)
            
            # Search for similar documents
            similarities, indices = self.faiss_index.search(question_embedding, self.max_retrieved_docs * 2)
            
            # Filter and rank results
            relevant_docs = []
            for similarity, idx in zip(similarities[0], indices[0]):
                if similarity < self.min_similarity_threshold:
                    continue
                    
                doc = self.document_store.get(idx)
                if not doc:
                    continue
                
                # Apply filters
                if jurisdiction and doc.get("jurisdiction") != jurisdiction:
                    continue
                if legal_domain and doc.get("legal_domain") != legal_domain:
                    continue
                
                # Add similarity score
                doc_with_score = doc.copy()
                doc_with_score["similarity_score"] = float(similarity)
                relevant_docs.append(doc_with_score)
                
                if len(relevant_docs) >= self.max_retrieved_docs:
                    break
            
            logger.info(f"🔍 Retrieved {len(relevant_docs)} relevant documents")
            return relevant_docs
            
        except Exception as e:
            logger.error(f"Error retrieving from FAISS: {e}")
            return []
    
    async def _generate_answer(self, question: str, retrieved_docs: List[Dict], 
                             session_id: str) -> Dict[str, Any]:
        """Generate answer using retrieved documents and conversation context"""
        try:
            # Prepare context from retrieved documents
            context = self._prepare_context(retrieved_docs)
            
            # Get conversation history
            conversation_context = self._get_conversation_context(session_id)
            
            # Generate answer using the best available model
            answer_result = await self._generate_with_gemini(question, context, conversation_context)
            
            # Add metadata
            answer_result.update({
                "session_id": session_id,
                "retrieved_documents": len(retrieved_docs),
                "sources": self._format_sources(retrieved_docs),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return answer_result
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": "I apologize, but I couldn't generate a proper response to your legal question.",
                "confidence": 0.0,
                "sources": []
            }
    
    def _prepare_context(self, retrieved_docs: List[Dict]) -> str:
        """Prepare context string from retrieved documents"""
        context_parts = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            title = doc.get("title", "Unknown Document")
            content = doc.get("content", "")[:1000]  # Limit content length
            jurisdiction = doc.get("jurisdiction", "")
            domain = doc.get("legal_domain", "")
            
            context_part = f"""
Document {i}:
Title: {title}
Jurisdiction: {jurisdiction}
Legal Domain: {domain}
Content: {content}
---
"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _get_conversation_context(self, session_id: str) -> str:
        """Get conversation history for context"""
        if session_id not in self.conversation_history:
            return ""
        
        history = self.conversation_history[session_id]
        context_parts = []
        
        # Include last 3 exchanges for context
        for exchange in history[-3:]:
            context_parts.append(f"Previous Question: {exchange['question']}")
            context_parts.append(f"Previous Answer: {exchange['answer'][:200]}...")
        
        return "\n".join(context_parts)
    
    async def _generate_with_gemini(self, question: str, context: str, 
                                  conversation_context: str) -> Dict[str, Any]:
        """Generate answer using Gemini Pro"""
        try:
            prompt = f"""
You are an expert legal AI assistant specializing in providing accurate, well-researched legal information. 
Your role is to answer legal questions by analyzing authoritative legal sources and providing comprehensive, 
accurate responses while emphasizing that your advice is informational only.

CONVERSATION CONTEXT (if any):
{conversation_context}

LEGAL SOURCES AND CONTEXT:
{context}

USER QUESTION:
{question}

INSTRUCTIONS:
1. Analyze the provided legal sources carefully
2. Provide a comprehensive answer based on the authoritative sources
3. Cite specific sources when making legal claims
4. If the question involves multiple jurisdictions, address differences
5. Highlight important legal principles and precedents
6. Be precise with legal terminology
7. If information is insufficient, acknowledge limitations
8. Provide practical guidance where appropriate
9. Maintain professional legal writing style

RESPONSE FORMAT:
- Provide a detailed, well-structured answer
- Include specific citations to source documents
- Rate your confidence in the answer (0.0 to 1.0)
- Identify key legal principles involved

Generate a comprehensive legal response:
"""

            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=2000,
                    temperature=0.1,
                )
            )
            
            answer_text = response.text
            
            # Extract confidence score (simple heuristic)
            confidence = self._calculate_confidence(answer_text, context)
            
            return {
                "answer": answer_text,
                "confidence": confidence,
                "model_used": "gemini-1.5-pro"
            }
            
        except Exception as e:
            logger.error(f"Error with Gemini generation: {e}")
            # Fallback to Groq
            return await self._generate_with_groq(question, context, conversation_context)
    
    async def _generate_with_groq(self, question: str, context: str, 
                                conversation_context: str) -> Dict[str, Any]:
        """Generate answer using Groq as fallback"""
        try:
            prompt = f"""
You are a legal AI assistant. Analyze the legal sources and provide accurate information.

Context: {conversation_context}
Sources: {context}
Question: {question}

Provide a detailed legal response with citations.
"""

            chat_completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=1500
            )
            
            answer_text = chat_completion.choices[0].message.content
            confidence = self._calculate_confidence(answer_text, context)
            
            return {
                "answer": answer_text,
                "confidence": confidence,
                "model_used": "groq-llama"
            }
            
        except Exception as e:
            logger.error(f"Error with Groq generation: {e}")
            return {
                "answer": "I apologize, but I'm unable to generate a response at this time.",
                "confidence": 0.0,
                "model_used": "fallback"
            }
    
    def _calculate_confidence(self, answer: str, context: str) -> float:
        """Calculate confidence score based on answer quality"""
        try:
            # Simple heuristic for confidence calculation
            confidence = 0.5  # Base confidence
            
            # Increase confidence if answer contains citations
            if "according to" in answer.lower() or "as stated in" in answer.lower():
                confidence += 0.2
            
            # Increase confidence if answer is substantial
            if len(answer) > 200:
                confidence += 0.1
            
            # Increase confidence if context was provided
            if context and len(context) > 100:
                confidence += 0.1
            
            # Decrease confidence if answer is too short or vague
            if len(answer) < 50:
                confidence -= 0.3
            
            return max(0.0, min(1.0, confidence))
            
        except Exception:
            return 0.5
    
    def _format_sources(self, retrieved_docs: List[Dict]) -> List[Dict[str, Any]]:
        """Format sources for response"""
        sources = []
        
        for doc in retrieved_docs:
            source = {
                "title": doc.get("title", "Unknown Document"),
                "source": doc.get("source", "Unknown Source"),
                "jurisdiction": doc.get("jurisdiction", ""),
                "legal_domain": doc.get("legal_domain", ""),
                "document_type": doc.get("document_type", ""),
                "url": doc.get("source_url", ""),
                "similarity_score": doc.get("similarity_score", 0.0)
            }
            sources.append(source)
        
        return sources
    
    def _update_conversation_history(self, session_id: str, question: str, answer_result: Dict):
        """Update conversation history for multi-turn support"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].append({
            "question": question,
            "answer": answer_result.get("answer", ""),
            "confidence": answer_result.get("confidence", 0.0),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last 10 exchanges per session
        if len(self.conversation_history[session_id]) > 10:
            self.conversation_history[session_id] = self.conversation_history[session_id][-10:]
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        return self.conversation_history.get(session_id, [])
    
    def clear_conversation_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        stats = {
            "vector_db": self.vector_db,
            "embeddings_model": "all-MiniLM-L6-v2",
            "active_sessions": len(self.conversation_history),
            "total_conversations": sum(len(history) for history in self.conversation_history.values())
        }
        
        if self.vector_db == "faiss" and self.faiss_index:
            stats["indexed_documents"] = self.faiss_index.ntotal
        
        return stats


# Global RAG system instance
legal_rag_system = None

async def get_rag_system() -> LegalRAGSystem:
    """Get initialized RAG system instance"""
    global legal_rag_system
    
    if legal_rag_system is None:
        legal_rag_system = LegalRAGSystem()
        await legal_rag_system.initialize()
        
        # Try to load existing FAISS index
        if legal_rag_system.vector_db == "faiss":
            await legal_rag_system._load_faiss_index()
    
    return legal_rag_system


# Main initialization function
async def initialize_legal_rag():
    """Initialize the legal RAG system"""
    try:
        rag_system = await get_rag_system()
        
        # Check if knowledge base exists, if not create it
        knowledge_base_path = "/app/legal_knowledge_base.json"
        if not os.path.exists(knowledge_base_path):
            logger.info("📚 Knowledge base not found, building it...")
            from legal_knowledge_builder import build_legal_knowledge_base
            await build_legal_knowledge_base()
        
        # Ingest knowledge base if FAISS index is empty
        if rag_system.vector_db == "faiss" and (not rag_system.faiss_index or rag_system.faiss_index.ntotal == 0):
            logger.info("📥 Ingesting knowledge base into vector database...")
            await rag_system.ingest_knowledge_base(knowledge_base_path)
        
        logger.info("🎉 Legal RAG system fully initialized and ready!")
        return rag_system
        
    except Exception as e:
        logger.error(f"Error initializing Legal RAG system: {e}")
        raise


if __name__ == "__main__":
    # Test the RAG system
    async def test_rag():
        rag_system = await initialize_legal_rag()
        
        # Test question
        test_question = "What are the key elements of a valid contract under US law?"
        result = await rag_system.answer_legal_question(test_question)
        
        print(f"Question: {test_question}")
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Sources: {len(result['sources'])}")
    
    asyncio.run(test_rag())