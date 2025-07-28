import os
import argparse
import json
import torch
from sentence_transformers import SentenceTransformer, InputExample
from torch.utils.data import DataLoader
from hybrid_retriever import AdapterFineTuner

def prepare_training_data(data_file):
    """Prepare training data for fine-tuning
    
    Args:
        data_file: Path to JSON file with training data
        
    Returns:
        List of InputExample objects for training
    """
    # Load training data
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    examples = []
    
    # Process each persona's relevant sections
    for persona, sections in data.get("personas", {}).items():
        # Get section IDs that are relevant for this persona
        relevant_ids = [section["id"] for section in sections]
        
        # Create positive and negative examples for contrastive learning
        for section in data.get("sections", []):
            section_id = section.get("id")
            section_text = section.get("content", "")
            
            # Skip if no content
            if not section_text:
                continue
            
            # Create positive example (persona should match this section)
            if section_id in relevant_ids:
                examples.append(
                    InputExample(
                        texts=[persona, section_text],
                        label=1.0  # Positive pair
                    )
                )
                
                # Create hard negative examples (sections that are not relevant for this persona)
                for neg_section in data.get("sections", []):
                    neg_id = neg_section.get("id")
                    neg_text = neg_section.get("content", "")
                    
                    if neg_id not in relevant_ids and neg_text and neg_id != section_id:
                        examples.append(
                            InputExample(
                                texts=[persona, neg_text],
                                label=0.0  # Negative pair
                            )
                        )
                        break  # Just one negative example per positive to balance dataset
    
    return examples

def finetune_retriever(data_file, output_dir, epochs=3, batch_size=16):
    """Fine-tune the retriever model with adapter modules
    
    Args:
        data_file: Path to JSON file with training data
        output_dir: Directory to save fine-tuned model
        epochs: Number of training epochs
        batch_size: Training batch size
    """
    print(f"Fine-tuning retriever model with data from {data_file}")
    
    # Prepare training data
    train_examples = prepare_training_data(data_file)
    print(f"Prepared {len(train_examples)} training examples")
    
    # Initialize fine-tuner
    fine_tuner = AdapterFineTuner(model_name='all-MiniLM-L6-v2')
    
    # Fine-tune the model
    print("Starting fine-tuning...")
    model = fine_tuner.fine_tune(train_examples, epochs=epochs, batch_size=batch_size)
    
    # Save the fine-tuned model
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, 'retriever')
    model.save(model_path)
    
    print(f"Fine-tuned model saved to {model_path}")

def main():
    """Main function to run fine-tuning"""
    parser = argparse.ArgumentParser(description="Fine-tune SmartPDFInsights models")
    parser.add_argument("--data", type=str, required=True, 
                        help="Path to JSON file with training data")
    parser.add_argument("--output", type=str, default="./models", 
                        help="Directory to save fine-tuned models")
    parser.add_argument("--epochs", type=int, default=3, 
                        help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=16, 
                        help="Training batch size")
    
    args = parser.parse_args()
    
    # Check if data file exists
    if not os.path.exists(args.data):
        print(f"Error: Data file '{args.data}' not found")
        return
    
    # Fine-tune retriever model
    finetune_retriever(args.data, args.output, args.epochs, args.batch_size)

if __name__ == "__main__":
    main()