"""
RAGAS Evaluation Script for RAG Quality Assessment.

Evaluates the RAG pipeline using metrics:
- Faithfulness: Is the answer grounded in the context?
- Answer Relevancy: Does the answer address the question?
- Context Precision: Are retrieved docs relevant?
- Context Recall: Were all relevant docs retrieved?

Usage:
    python scripts/evaluate_rag.py --samples 10
    python scripts/evaluate_rag.py --dataset custom_questions.json
"""

import argparse
import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from src.core.config import settings
from src.core.logging import get_logger
from src.services.neo4j_service import neo4j_service
from src.services.qa_service import QAService
from src.services.qdrant_service import qdrant_service

logger = get_logger(__name__)

# Sample evaluation questions with expected answers
SAMPLE_QUESTIONS = [
    {
        "question": "Who are the DevOps Engineers?",
        "ground_truth": "DevOps Engineers include employees with the title 'DevOps Engineer' in the organization."
    },
    {
        "question": "What projects are currently active?",
        "ground_truth": "Active projects are those with status 'active' in the database."
    },
    {
        "question": "Who knows Python programming?",
        "ground_truth": "Employees who have Python listed as one of their skills."
    },
    {
        "question": "Which department has the most employees?",
        "ground_truth": "The department with the highest employee count."
    },
    {
        "question": "What skills are most common in Engineering?",
        "ground_truth": "Technical skills like Python, JavaScript, and cloud technologies are common in Engineering."
    },
]


def get_llm():
    """Get LLM for RAGAS evaluation."""
    llm_config = settings.get_llm_config()
    if llm_config["provider"] == "openai":
        return ChatOpenAI(
            api_key=llm_config["api_key"],
            model=llm_config["model"],
            temperature=0
        )
    else:
        return ChatGroq(
            api_key=llm_config["api_key"],
            model_name=llm_config["model"],
            temperature=0
        )


def run_query(qa_service: QAService, question: str) -> Dict[str, Any]:
    """Run a query and capture answer + contexts."""
    try:
        result = qa_service.query(question=question, include_cypher=False)
        return {
            "answer": result.get("answer", ""),
            "contexts": result.get("metadata", {}).get("context_used", []),
            "confidence": result.get("confidence", {}),
        }
    except Exception as e:
        logger.error(f"Query failed: {e}")
        return {"answer": str(e), "contexts": [], "confidence": {}}


def prepare_evaluation_dataset(
    qa_service: QAService,
    questions: List[Dict[str, str]],
    use_qdrant: bool = True
) -> Dataset:
    """
    Prepare evaluation dataset by running queries.
    
    Args:
        qa_service: QA service instance
        questions: List of {question, ground_truth} dicts
        use_qdrant: Whether to use Qdrant for retrieval
        
    Returns:
        HuggingFace Dataset for RAGAS evaluation
    """
    logger.info(f"Preparing evaluation dataset with {len(questions)} questions...")
    
    # Set retrieval backend
    qa_service._use_qdrant = use_qdrant
    
    data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
    }
    
    for i, q in enumerate(questions):
        question = q["question"]
        ground_truth = q.get("ground_truth", "")
        
        logger.info(f"[{i+1}/{len(questions)}] Processing: {question[:50]}...")
        
        result = run_query(qa_service, question)
        
        data["question"].append(question)
        data["answer"].append(result["answer"])
        data["contexts"].append(result["contexts"] if result["contexts"] else ["No context retrieved"])
        data["ground_truth"].append(ground_truth)
    
    return Dataset.from_dict(data)


def run_evaluation(
    dataset: Dataset,
    metrics: Optional[List] = None
) -> Dict[str, float]:
    """
    Run RAGAS evaluation on the dataset.
    
    Args:
        dataset: Prepared evaluation dataset
        metrics: List of metrics to evaluate (default: all)
        
    Returns:
        Dict of metric scores
    """
    if metrics is None:
        metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ]
    
    logger.info(f"Running RAGAS evaluation with {len(metrics)} metrics...")
    
    try:
        result = evaluate(
            dataset,
            metrics=metrics,
            llm=get_llm(),
        )
        
        scores = {
            metric.__class__.__name__: float(result[metric.__class__.__name__])
            for metric in metrics
            if metric.__class__.__name__ in result
        }
        
        return scores
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return {"error": str(e)}


def save_results(
    scores: Dict[str, float],
    dataset: Dataset,
    output_path: str
):
    """Save evaluation results to JSON."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "scores": scores,
        "num_samples": len(dataset),
        "details": {
            "questions": dataset["question"],
            "answers": dataset["answer"],
        }
    }
    
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to {output_path}")


def print_results(scores: Dict[str, float]):
    """Print evaluation results in a formatted way."""
    print("\n" + "=" * 50)
    print("📊 RAGAS Evaluation Results")
    print("=" * 50)
    
    if "error" in scores:
        print(f"❌ Error: {scores['error']}")
        return
    
    for metric, score in scores.items():
        # Color coding based on score
        if score >= 0.8:
            indicator = "🟢"
        elif score >= 0.5:
            indicator = "🟡"
        else:
            indicator = "🔴"
        
        print(f"{indicator} {metric}: {score:.4f}")
    
    # Calculate average
    avg = sum(scores.values()) / len(scores) if scores else 0
    print("-" * 50)
    print(f"📈 Average Score: {avg:.4f}")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="RAGAS Evaluation for RAG Pipeline")
    parser.add_argument(
        "--samples", 
        type=int, 
        default=5,
        help="Number of sample questions to evaluate"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        help="Path to custom questions JSON file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="scripts/ragas_results.json",
        help="Output path for results"
    )
    parser.add_argument(
        "--use-qdrant",
        action="store_true",
        default=True,
        help="Use Qdrant for retrieval (default: True)"
    )
    parser.add_argument(
        "--use-neo4j",
        action="store_true",
        help="Use Neo4j vectors instead of Qdrant"
    )
    
    args = parser.parse_args()
    
    # Load questions
    if args.dataset:
        with open(args.dataset, "r") as f:
            questions = json.load(f)
        logger.info(f"Loaded {len(questions)} questions from {args.dataset}")
    else:
        questions = SAMPLE_QUESTIONS[:args.samples]
        logger.info(f"Using {len(questions)} sample questions")
    
    # Initialize services
    logger.info("Initializing services...")
    graph = neo4j_service.get_graph()
    qa_service = QAService(graph)
    
    # Check Qdrant health
    if not args.use_neo4j:
        if qdrant_service.health_check():
            logger.info("✅ Qdrant is healthy")
        else:
            logger.warning("⚠️ Qdrant not available, falling back to Neo4j")
            args.use_neo4j = True
    
    use_qdrant = not args.use_neo4j
    logger.info(f"Using {'Qdrant' if use_qdrant else 'Neo4j'} for retrieval")
    
    # Prepare dataset
    dataset = prepare_evaluation_dataset(qa_service, questions, use_qdrant)
    
    # Run evaluation
    scores = run_evaluation(dataset)
    
    # Print and save results
    print_results(scores)
    save_results(scores, dataset, args.output)
    
    return scores


if __name__ == "__main__":
    main()
