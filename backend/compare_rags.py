from dotenv import load_dotenv
from core_highlevel_chain import run_llm as run_highlevel
from core_custom_chain import run_llm as run_custom
from langchain_openai import ChatOpenAI
import time
import re

load_dotenv()

# Test queries - mix of different types
test_queries = [
    # Specific technical questions
    "what are the most important facts to know about MCP during a tech interview?",
    "explain the key components of MCP architecture",
    
    # Questions that might not be in the knowledge base
    "what is the relationship between MCP and quantum computing?",
    
    # Questions requiring detailed answers
    "how does MCP handle error recovery and fault tolerance?",
    
    # Simple factual questions
    "what does MCP stand for?"
]

def evaluate_answer_quality(query, answer, llm):
    """Use LLM to evaluate answer quality on multiple dimensions"""
    
    eval_prompt = f"""Evaluate this RAG-generated answer on a scale of 1-10 for each metric:

Question: {query}
Answer: {answer}

Metrics:
1. Relevance (1-10): Does the answer directly address the question?
2. Completeness (1-10): Does it cover all aspects of the question?
3. Specificity (1-10): Does it provide specific details vs generic information?
4. Confidence (1-10): Does it appropriately express uncertainty when needed?
5. Hallucination Risk (1-10): 10=no hallucination risk, 1=likely hallucinated

Provide ONLY the scores in this format:
Relevance: X
Completeness: X
Specificity: X
Confidence: X
Hallucination: X
"""
    
    try:
        response = llm.invoke(eval_prompt)
        scores = {}
        for line in response.content.split('\n'):
            if ':' in line:
                metric, score = line.split(':')
                scores[metric.strip().lower()] = float(score.strip())
        return scores
    except:
        return {'relevance': 0, 'completeness': 0, 'specificity': 0, 'confidence': 0, 'hallucination': 0}

def analyze_answer_characteristics(answer):
    """Extract objective characteristics from the answer"""
    return {
        'length': len(answer),
        'admits_uncertainty': any(phrase in answer.lower() for phrase in ["don't know", "uncertain", "not sure", "no information"]),
        'has_examples': bool(re.search(r'(for example|e\.g\.|such as|including)', answer, re.IGNORECASE)),
        'has_structure': bool(re.search(r'(\d+\.|bullet|first|second|finally)', answer, re.IGNORECASE)),
        'error': answer.startswith("Error:")
    }

def compare_results():
    llm = ChatOpenAI(temperature=0, mod3el="gpt-4o-mini")  # For evaluation
    
    all_results = []
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"QUERY: {query}")
        print('='*80)
        
        # Run both chains
        start = time.time()
        try:
            highlevel_result = run_highlevel(query)
            highlevel_answer = highlevel_result.get("answer", "No answer")
            highlevel_time = time.time() - start
        except Exception as e:
            highlevel_answer = f"Error: {str(e)}"
            highlevel_time = 0
        
        start = time.time()
        try:
            custom_result = run_custom(query)
            custom_answer = custom_result.content if hasattr(custom_result, 'content') else str(custom_result)
            custom_time = time.time() - start
        except Exception as e:
            custom_answer = f"Error: {str(e)}"
            custom_time = 0
        
        # Analyze answers
        highlevel_chars = analyze_answer_characteristics(highlevel_answer)
        custom_chars = analyze_answer_characteristics(custom_answer)
        
        # Get quality scores
        highlevel_scores = evaluate_answer_quality(query, highlevel_answer, llm)
        custom_scores = evaluate_answer_quality(query, custom_answer, llm)
        
        # Display results
        print(f"\nHIGHLEVEL CHAIN:")
        print(f"Answer preview: {highlevel_answer[:200]}...")
        print(f"Characteristics: Length={highlevel_chars['length']}, "
              f"Admits uncertainty={highlevel_chars['admits_uncertainty']}, "
              f"Has examples={highlevel_chars['has_examples']}")
        print(f"Quality scores: {highlevel_scores}")
        
        print(f"\nCUSTOM CHAIN:")
        print(f"Answer preview: {custom_answer[:200]}...")
        print(f"Characteristics: Length={custom_chars['length']}, "
              f"Admits uncertainty={custom_chars['admits_uncertainty']}, "
              f"Has examples={custom_chars['has_examples']}")
        print(f"Quality scores: {custom_scores}")
        
        # Store results
        all_results.append({
            'query': query,
            'highlevel_scores': highlevel_scores,
            'custom_scores': custom_scores,
            'highlevel_chars': highlevel_chars,
            'custom_chars': custom_chars,
            'highlevel_time': highlevel_time,
            'custom_time': custom_time
        })
    
    # Calculate decision metrics
    print(f"\n{'='*80}")
    print("DECISION METRICS")
    print('='*80)
    
    # Average quality scores
    metrics = ['relevance', 'completeness', 'specificity', 'confidence', 'hallucination']
    highlevel_avg = {}
    custom_avg = {}
    
    for metric in metrics:
        highlevel_avg[metric] = sum(r['highlevel_scores'].get(metric, 0) for r in all_results) / len(all_results)
        custom_avg[metric] = sum(r['custom_scores'].get(metric, 0) for r in all_results) / len(all_results)
    
    print("\nQUALITY SCORES (higher is better):")
    for metric in metrics:
        winner = "→" if abs(highlevel_avg[metric] - custom_avg[metric]) < 0.5 else ("✓" if highlevel_avg[metric] > custom_avg[metric] else "✗")
        print(f"{metric.capitalize():15} Highlevel: {highlevel_avg[metric]:.1f} {winner} Custom: {custom_avg[metric]:.1f}")
    
    # Reliability metrics
    highlevel_errors = sum(r['highlevel_chars']['error'] for r in all_results)
    custom_errors = sum(r['custom_chars']['error'] for r in all_results)
    highlevel_uncertain = sum(r['highlevel_chars']['admits_uncertainty'] for r in all_results)
    custom_uncertain = sum(r['custom_chars']['admits_uncertainty'] for r in all_results)
    
    print("\nRELIABILITY:")
    print(f"Error rate:        Highlevel: {highlevel_errors}/{len(all_results)} vs Custom: {custom_errors}/{len(all_results)}")
    print(f"Admits uncertainty: Highlevel: {highlevel_uncertain}/{len(all_results)} vs Custom: {custom_uncertain}/{len(all_results)}")
    
    # Performance
    avg_highlevel_time = sum(r['highlevel_time'] for r in all_results) / len(all_results)
    avg_custom_time = sum(r['custom_time'] for r in all_results) / len(all_results)
    print(f"\nPERFORMANCE:")
    print(f"Avg response time: Highlevel: {avg_highlevel_time:.2f}s vs Custom: {avg_custom_time:.2f}s")
    
    # Overall recommendation
    print(f"\n{'='*80}")
    print("RECOMMENDATION")
    print('='*80)
    
    highlevel_score = sum(highlevel_avg.values()) / len(highlevel_avg)
    custom_score = sum(custom_avg.values()) / len(custom_avg)
    
    if highlevel_score > custom_score + 1:
        print(f"✓ USE HIGHLEVEL CHAIN - Better overall quality ({highlevel_score:.1f} vs {custom_score:.1f})")
    elif custom_score > highlevel_score + 1:
        print(f"✓ USE CUSTOM CHAIN - Better overall quality ({custom_score:.1f} vs {highlevel_score:.1f})")
    else:
        # Tie breaker based on use case
        print("≈ CHAINS ARE SIMILAR - Choose based on your priorities:")
        if avg_custom_time < avg_highlevel_time * 0.7:
            print("  → Custom chain if SPEED is critical")
        if highlevel_avg['hallucination'] > custom_avg['hallucination']:
            print("  → Highlevel chain if SAFETY is critical")
        if highlevel_avg['completeness'] > custom_avg['completeness']:
            print("  → Highlevel chain if COMPREHENSIVE answers needed")
        if custom_uncertain < highlevel_uncertain:
            print("  → Custom chain if you prefer CONFIDENT answers")

if __name__ == "__main__":
    compare_results()