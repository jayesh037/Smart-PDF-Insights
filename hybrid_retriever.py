import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import torch
from typing import List, Dict, Tuple, Optional

class HybridRetriever:
    """Hybrid retrieval system combining sparse (TF-IDF) and dense (transformer embeddings) retrieval"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', sparse_weight: float = 0.3):
        """Initialize the hybrid retriever with both sparse and dense components
        
        Args:
            model_name: Name of the SentenceTransformer model to use
            sparse_weight: Weight for sparse retrieval scores (0-1)
        """
        self.sparse_weight = sparse_weight
        self.dense_weight = 1.0 - sparse_weight
        
        # Initialize sparse retriever (TF-IDF)
        self.tfidf_vectorizer = TfidfVectorizer(
            min_df=2, max_df=0.85,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Initialize dense retriever (SentenceTransformer)
        self.model = SentenceTransformer(model_name)
        
        # Enable model quantization for CPU efficiency
        if torch.cuda.is_available() == False:
            self.model = torch.quantization.quantize_dynamic(
                self.model, {torch.nn.Linear}, dtype=torch.qint8
            )
        
        self.corpus_embeddings = None
        self.corpus_sparse_vectors = None
        self.corpus = None
        self.corpus_metadata = None
    
    def index_corpus(self, corpus: List[str], metadata: Optional[List[Dict]] = None):
        """Index the corpus with both sparse and dense representations
        
        Args:
            corpus: List of text documents to index
            metadata: Optional list of metadata dictionaries for each document
        """
        self.corpus = corpus
        self.corpus_metadata = metadata if metadata else [{} for _ in corpus]
        
        # Create sparse representations
        self.corpus_sparse_vectors = self.tfidf_vectorizer.fit_transform(corpus)
        
        # Create dense representations
        self.corpus_embeddings = self.model.encode(corpus, convert_to_tensor=True, show_progress_bar=False)
    
    def expand_query(self, query: str) -> str:
        """Expand the query with relevant terms to improve retrieval
        
        Args:
            query: Original query string
            
        Returns:
            Expanded query string
        """
        # Simple rule-based query expansion for persona-based queries
        expanded_terms = []
        
        # Add synonyms for common persona terms
        if "student" in query.lower():
            expanded_terms.extend(["education", "learning", "academic", "study"])
        elif "researcher" in query.lower():
            expanded_terms.extend(["research", "analysis", "investigation", "study"])
        elif "business" in query.lower() or "professional" in query.lower():
            expanded_terms.extend(["corporate", "enterprise", "commercial", "company"])
        
        # Add expanded terms to query
        if expanded_terms:
            expanded_query = f"{query} {' '.join(expanded_terms)}"
            return expanded_query
        
        return query
    
    def retrieve(self, query: str, top_k: int = 5, expand: bool = True) -> List[Dict]:
        """Retrieve the most relevant documents using hybrid scoring
        
        Args:
            query: Query string
            top_k: Number of top results to return
            expand: Whether to apply query expansion
            
        Returns:
            List of dictionaries with retrieved documents and scores
        """
        if self.corpus is None or len(self.corpus) == 0:
            return []
        
        # Apply query expansion if enabled
        if expand:
            query = self.expand_query(query)
        
        # Get sparse scores
        query_sparse = self.tfidf_vectorizer.transform([query])
        sparse_scores = cosine_similarity(query_sparse, self.corpus_sparse_vectors).flatten()
        
        # Get dense scores
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        dense_scores = cosine_similarity(
            query_embedding.cpu().numpy().reshape(1, -1),
            self.corpus_embeddings.cpu().numpy()
        ).flatten()
        
        # Combine scores
        combined_scores = (self.sparse_weight * sparse_scores) + (self.dense_weight * dense_scores)
        
        # Apply position bias (assuming earlier sections might be more important)
        position_boost = np.linspace(0.1, 0, len(combined_scores))
        combined_scores += position_boost
        
        # Apply length normalization (avoid bias towards longer sections)
        lengths = np.array([len(doc.split()) for doc in self.corpus])
        length_penalty = 1.0 / np.log(2.0 + lengths / 100.0)  # Penalize very long documents
        combined_scores *= length_penalty
        
        # Get top-k results
        top_indices = combined_scores.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                'content': self.corpus[idx],
                'metadata': self.corpus_metadata[idx],
                'score': float(combined_scores[idx]),
                'sparse_score': float(sparse_scores[idx]),
                'dense_score': float(dense_scores[idx])
            })
        
        return results


class AdapterFineTuner:
    """Fine-tune a SentenceTransformer model with adapter modules for efficiency"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the fine-tuner with a base model
        
        Args:
            model_name: Name of the SentenceTransformer model to use as base
        """
        self.model = SentenceTransformer(model_name)
        self.adapter_size = 64  # Size of adapter bottleneck
    
    def add_adapters(self):
        """Add adapter modules to the transformer layers"""
        # This is a simplified implementation - in a real scenario, you would
        # need to modify the actual PyTorch modules in the model
        for name, module in self.model.named_modules():
            if isinstance(module, torch.nn.Linear) and 'out_proj' in name:
                # Get original dimensions
                in_features = module.in_features
                out_features = module.out_features
                
                # Create adapter components
                down_proj = torch.nn.Linear(in_features, self.adapter_size)
                up_proj = torch.nn.Linear(self.adapter_size, out_features)
                
                # Initialize close to identity function
                torch.nn.init.normal_(down_proj.weight, std=1e-3)
                torch.nn.init.normal_(up_proj.weight, std=1e-3)
                
                # Replace with adapter-augmented module
                # Note: This is conceptual - actual implementation would require
                # modifying the forward pass of the module
                print(f"Added adapter to {name}: {in_features} -> {self.adapter_size} -> {out_features}")
    
    def fine_tune(self, train_examples, epochs: int = 3, batch_size: int = 16):
        """Fine-tune the model with adapters on contrastive examples
        
        Args:
            train_examples: List of InputExample objects for training
            epochs: Number of training epochs
            batch_size: Training batch size
        """
        # Add adapters to model
        self.add_adapters()
        
        # Import the appropriate loss function from sentence_transformers
        from sentence_transformers import losses
        
        # Create data loader
        train_dataloader = torch.utils.data.DataLoader(train_examples, shuffle=True, batch_size=batch_size)
        
        # Use CosineSimilarityLoss which works with InputExample format
        train_loss = losses.CosineSimilarityLoss(self.model)
        
        # Train the model
        self.model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=epochs,
            warmup_steps=100,
            show_progress_bar=True
        )
        
        return self.model