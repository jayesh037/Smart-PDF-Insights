import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import numpy as np
from typing import List, Dict, Optional, Union, Tuple

class ContextAwareSummarizer:
    """Context-aware summarization using pre-trained models with quantization for CPU efficiency"""
    
    def __init__(self, model_name: str = 'facebook/bart-base'):
        """Initialize the summarizer with a pre-trained model
        
        Args:
            model_name: Name of the model to use (facebook/bart-base recommended for CPU)
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        # Apply quantization for CPU efficiency
        if not torch.cuda.is_available():
            self.model = torch.quantization.quantize_dynamic(
                self.model, {torch.nn.Linear}, dtype=torch.qint8
            )
    
    def generate_summary(self, text: str, persona: str, max_length: int = 150, 
                         min_length: int = 40, num_beams: int = 4) -> str:
        """Generate a context-aware summary tailored to the persona
        
        Args:
            text: Text to summarize
            persona: Description of the target persona
            max_length: Maximum summary length
            min_length: Minimum summary length
            num_beams: Number of beams for beam search
            
        Returns:
            Generated summary
        """
        # Create a context-aware prompt
        prompt = self._create_prompt(text, persona)
        
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
        
        # Generate summary
        summary_ids = self.model.generate(
            inputs["input_ids"],
            max_length=max_length,
            min_length=min_length,
            num_beams=num_beams,
            early_stopping=True,
            no_repeat_ngram_size=2,
            length_penalty=2.0
        )
        
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        # Post-process summary
        summary = self._post_process_summary(summary, persona)
        
        return summary
    
    def _create_prompt(self, text: str, persona: str) -> str:
        """Create a context-aware prompt for the model
        
        Args:
            text: Text to summarize
            persona: Description of the target persona
            
        Returns:
            Formatted prompt
        """
        # Create a prompt with persona information
        prompt = f"Summarize the following text for a {persona}: {text}"
        
        return prompt
    
    def _post_process_summary(self, summary: str, persona: str) -> str:
        """Apply post-processing to improve summary quality
        
        Args:
            summary: Raw generated summary
            persona: Description of the target persona
            
        Returns:
            Post-processed summary
        """
        # Remove any repetitive phrases
        sentences = summary.split(". ")
        unique_sentences = []
        for s in sentences:
            if s not in unique_sentences:
                unique_sentences.append(s)
        
        # Rejoin sentences
        summary = ". ".join(unique_sentences)
        
        # Ensure proper ending punctuation
        if summary and not summary.endswith(('.', '!', '?')):
            summary += '.'
        
        return summary
    
    def generate_two_stage_summary(self, text: str, persona: str, 
                                  max_length: int = 150) -> str:
        """Generate a summary using a two-stage approach for better quality
        
        Args:
            text: Text to summarize
            persona: Description of the target persona
            max_length: Maximum summary length
            
        Returns:
            Generated summary
        """
        # Stage 1: Extract key points (extractive summary)
        # For simplicity, we'll use sentence scoring based on keyword matching
        sentences = text.split(". ")
        
        # Define persona-specific keywords
        keywords = self._get_persona_keywords(persona)
        
        # Score sentences based on keyword presence
        scores = []
        for sentence in sentences:
            score = sum(1 for keyword in keywords if keyword.lower() in sentence.lower())
            scores.append(score)
        
        # Get top sentences (up to 1/3 of the original text)
        top_indices = np.argsort(scores)[-len(sentences)//3:][::-1]
        top_indices = sorted(top_indices)  # Sort by position to maintain flow
        
        # Create extractive summary
        extractive_summary = ". ".join([sentences[i] for i in top_indices])
        
        # Stage 2: Generate abstractive summary from the extractive summary
        final_summary = self.generate_summary(
            extractive_summary, persona, max_length=max_length
        )
        
        return final_summary
    
    def _get_persona_keywords(self, persona: str) -> List[str]:
        """Get keywords relevant to a specific persona
        
        Args:
            persona: Description of the target persona
            
        Returns:
            List of relevant keywords
        """
        # Basic keyword mapping for common personas
        keyword_map = {
            "student": ["learn", "study", "education", "academic", "school", "university", 
                       "knowledge", "course", "assignment", "research", "project"],
            
            "researcher": ["research", "study", "analysis", "data", "method", "result", 
                          "finding", "conclusion", "evidence", "hypothesis", "experiment"],
            
            "business professional": ["business", "market", "strategy", "company", "industry", 
                                     "profit", "revenue", "customer", "product", "service", 
                                     "management", "investment", "growth"],
            
            "general reader": ["overview", "summary", "important", "key", "main", 
                              "highlight", "essential", "significant", "notable"]
        }
        
        # Find the best matching persona
        best_match = "general reader"  # Default
        for key in keyword_map:
            if key.lower() in persona.lower():
                best_match = key
                break
        
        return keyword_map[best_match]


class EvaluationMetrics:
    """Evaluation metrics for heading extraction and relevance ranking"""
    
    @staticmethod
    def evaluate_heading_extraction(predicted_headings: List[Dict], 
                                   ground_truth_headings: List[Dict]) -> Dict:
        """Evaluate heading extraction performance
        
        Args:
            predicted_headings: List of predicted heading dictionaries
            ground_truth_headings: List of ground truth heading dictionaries
            
        Returns:
            Dictionary with precision, recall, and F1 metrics
        """
        # Extract text from headings for comparison
        pred_texts = [h["text"].lower().strip() for h in predicted_headings]
        gt_texts = [h["text"].lower().strip() for h in ground_truth_headings]
        
        # Calculate true positives, false positives, false negatives
        tp = sum(1 for p in pred_texts if p in gt_texts)
        fp = sum(1 for p in pred_texts if p not in gt_texts)
        fn = sum(1 for g in gt_texts if g not in pred_texts)
        
        # Calculate metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn
        }
    
    @staticmethod
    def evaluate_relevance_ranking(predicted_rankings: List[Dict], 
                                 ground_truth_rankings: List[Dict],
                                 k_values: List[int] = [1, 3, 5]) -> Dict:
        """Evaluate relevance ranking performance
        
        Args:
            predicted_rankings: List of predicted section dictionaries with scores
            ground_truth_rankings: List of ground truth relevant section dictionaries
            k_values: List of k values for precision@k and recall@k
            
        Returns:
            Dictionary with precision@k, recall@k, and MAP metrics
        """
        # Sort predicted rankings by score in descending order
        sorted_predictions = sorted(predicted_rankings, key=lambda x: x.get("score", 0), reverse=True)
        
        # Extract content IDs for comparison
        pred_ids = [p.get("id", p.get("content", "")) for p in sorted_predictions]
        gt_ids = [g.get("id", g.get("content", "")) for g in ground_truth_rankings]
        
        # Calculate metrics for each k
        results = {}
        for k in k_values:
            if k > len(pred_ids):
                continue
                
            # Precision@k: proportion of relevant items in top-k results
            precision_k = sum(1 for p in pred_ids[:k] if p in gt_ids) / k
            
            # Recall@k: proportion of relevant items found in top-k results
            recall_k = sum(1 for p in pred_ids[:k] if p in gt_ids) / len(gt_ids) if gt_ids else 0
            
            results[f"precision@{k}"] = precision_k
            results[f"recall@{k}"] = recall_k
        
        # Calculate Mean Average Precision (MAP)
        ap = 0.0
        relevant_count = 0
        
        for i, pred_id in enumerate(pred_ids):
            if pred_id in gt_ids:
                relevant_count += 1
                ap += relevant_count / (i + 1)
        
        map_score = ap / len(gt_ids) if gt_ids else 0
        results["map"] = map_score
        
        return results