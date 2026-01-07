"""
Backend API Benchmark Script

Tests API response times for various query types.
Measures latency, throughput, and identifies slow queries.

Usage:
    python scripts/benchmark_api.py
"""

import time
import statistics
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
NUM_ITERATIONS = 5  # Runs per query
CONCURRENT_USERS = 3  # Parallel requests for load testing

# Test queries - mix of simple and complex
TEST_QUERIES = [
    # Simple counts
    "How many employees are there?",
    "How many departments do we have?",
    "How many projects are active?",
    
    # Filtering queries
    "Who has Python skills?",
    "Show me employees in Engineering",
    "List senior level employees",
    
    # Aggregation queries
    "What is the average salary by department?",
    "Count employees by location",
    
    # Relationship traversal
    "Who reports to whom?",
    "Which employees work on active projects?",
    
    # Complex queries
    "Find Python experts in Engineering",
    "Show me senior engineers with AWS skills",
]


def benchmark_single_query(question: str) -> Dict[str, Any]:
    """Benchmark a single query and return timing info."""
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": question, "include_cypher": True},
            timeout=60
        )
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # Convert to ms
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "duration_ms": duration,
                "answer_length": len(data.get("answer", "")),
                "cypher": data.get("cypher_query", ""),
            }
        else:
            return {
                "success": False,
                "duration_ms": duration,
                "error": f"HTTP {response.status_code}",
            }
    except requests.exceptions.Timeout:
        return {"success": False, "duration_ms": 60000, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "duration_ms": 0, "error": str(e)}


def benchmark_health() -> Dict[str, float]:
    """Benchmark health endpoints."""
    results = {}
    
    # Health check
    start = time.time()
    requests.get(f"{API_BASE_URL}/health")
    results["health_check_ms"] = (time.time() - start) * 1000
    
    # Schema endpoint
    start = time.time()
    requests.get(f"{API_BASE_URL}/health/schema")
    results["schema_ms"] = (time.time() - start) * 1000
    
    return results


def run_benchmark(queries: List[str], iterations: int = 5) -> Dict[str, Any]:
    """Run full benchmark suite."""
    print("=" * 60)
    print("🚀 BACKEND API BENCHMARK")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  • API URL: {API_BASE_URL}")
    print(f"  • Queries: {len(queries)}")
    print(f"  • Iterations per query: {iterations}")
    print()
    
    # Test connectivity first
    print("🔗 Testing connectivity...")
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health.status_code != 200:
            print(f"❌ API not healthy: {health.status_code}")
            return None
        print("  ✓ API is healthy\n")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure the backend is running: uvicorn src.main:app --reload")
        return None
    
    # Benchmark health endpoints
    print("📊 Benchmarking health endpoints...")
    health_results = benchmark_health()
    for endpoint, duration in health_results.items():
        print(f"  • {endpoint}: {duration:.1f}ms")
    print()
    
    # Benchmark queries
    print("📋 Benchmarking queries...")
    print("-" * 60)
    
    all_results = []
    
    for i, query in enumerate(queries, 1):
        query_times = []
        successes = 0
        
        for _ in range(iterations):
            result = benchmark_single_query(query)
            if result["success"]:
                query_times.append(result["duration_ms"])
                successes += 1
        
        if query_times:
            avg_time = statistics.mean(query_times)
            min_time = min(query_times)
            max_time = max(query_times)
            
            # Status indicator
            if avg_time < 1000:
                status = "🟢"
            elif avg_time < 3000:
                status = "🟡"
            else:
                status = "🔴"
            
            print(f"{status} [{i:2d}/{len(queries)}] {query[:45]:<45} | avg: {avg_time:>7.0f}ms | min: {min_time:>6.0f}ms | max: {max_time:>6.0f}ms")
            
            all_results.append({
                "query": query,
                "avg_ms": avg_time,
                "min_ms": min_time,
                "max_ms": max_time,
                "success_rate": successes / iterations
            })
        else:
            print(f"🔴 [{i:2d}/{len(queries)}] {query[:45]:<45} | FAILED")
            all_results.append({
                "query": query,
                "avg_ms": None,
                "success_rate": 0
            })
    
    # Summary
    print()
    print("=" * 60)
    print("📈 BENCHMARK SUMMARY")
    print("=" * 60)
    
    successful = [r for r in all_results if r.get("avg_ms")]
    if successful:
        all_times = [r["avg_ms"] for r in successful]
        
        print(f"\n  Total Queries:     {len(queries)}")
        print(f"  Successful:        {len(successful)}")
        print(f"  Failed:            {len(queries) - len(successful)}")
        print()
        print(f"  Average Response:  {statistics.mean(all_times):.0f}ms")
        print(f"  Median Response:   {statistics.median(all_times):.0f}ms")
        print(f"  Fastest Query:     {min(all_times):.0f}ms")
        print(f"  Slowest Query:     {max(all_times):.0f}ms")
        print()
        
        # Performance rating
        avg = statistics.mean(all_times)
        if avg < 1000:
            print("  📊 Performance Rating: EXCELLENT ⭐⭐⭐")
        elif avg < 2000:
            print("  📊 Performance Rating: GOOD ⭐⭐")
        elif avg < 5000:
            print("  📊 Performance Rating: ACCEPTABLE ⭐")
        else:
            print("  📊 Performance Rating: NEEDS OPTIMIZATION ⚠️")
        
        # Slowest queries
        slowest = sorted(successful, key=lambda x: x["avg_ms"], reverse=True)[:3]
        print("\n  🐢 Slowest Queries:")
        for r in slowest:
            print(f"     • {r['avg_ms']:.0f}ms: {r['query'][:50]}")
    
    print()
    print("=" * 60)
    
    return all_results


def load_test(query: str, num_concurrent: int = 5, duration_seconds: int = 10):
    """Run concurrent load test on a single query."""
    print(f"\n⚡ LOAD TEST")
    print(f"   Query: {query}")
    print(f"   Concurrent users: {num_concurrent}")
    print(f"   Duration: {duration_seconds}s")
    print()
    
    results = []
    end_time = time.time() + duration_seconds
    
    def worker():
        while time.time() < end_time:
            result = benchmark_single_query(query)
            results.append(result)
    
    with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [executor.submit(worker) for _ in range(num_concurrent)]
        for f in futures:
            f.result()
    
    successful = [r for r in results if r["success"]]
    if successful:
        times = [r["duration_ms"] for r in successful]
        requests_per_sec = len(successful) / duration_seconds
        
        print(f"   ✓ Total Requests:    {len(results)}")
        print(f"   ✓ Successful:        {len(successful)}")
        print(f"   ✓ Requests/second:   {requests_per_sec:.1f}")
        print(f"   ✓ Avg Response:      {statistics.mean(times):.0f}ms")
        print(f"   ✓ P95 Response:      {sorted(times)[int(len(times)*0.95)]:.0f}ms")
    else:
        print("   ❌ All requests failed")


if __name__ == "__main__":
    # Run query benchmark
    results = run_benchmark(TEST_QUERIES, NUM_ITERATIONS)
    
    # Optional: Run load test
    print("\nRun load test? (Enter query number 1-{} or 'skip'): ".format(len(TEST_QUERIES)), end="")
    try:
        choice = input().strip()
        if choice.isdigit() and 1 <= int(choice) <= len(TEST_QUERIES):
            load_test(TEST_QUERIES[int(choice)-1], CONCURRENT_USERS, 10)
    except:
        pass
