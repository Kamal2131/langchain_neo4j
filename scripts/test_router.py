"""Test query router classification."""
import sys
sys.path.insert(0, '.')

from src.services.query_router import QueryRouter

router = QueryRouter(use_llm=False)

test_queries = [
    ("List all projects", "graph"),
    ("Show me all DevOps Engineers", "graph"),
    ("How many employees in Engineering?", "graph"),
    ("Summarize the contract", "vector"),
    ("What does the policy say about vacation?", "vector"),
    ("Explain the project scope", "vector"),
    ("Who leads Project Alpha and what are its goals?", "hybrid"),
    ("Tell me about John's experience", "hybrid"),
]

print("=" * 50)
print("🧪 Query Router Classification Tests")
print("=" * 50)

passed = 0
for query, expected in test_queries:
    result = router.route(query)
    actual = result.query_type.value
    status = "✅" if actual == expected else "❌"
    if actual == expected:
        passed += 1
    print(f"{status} '{query[:35]}...' -> {actual} (expected: {expected})")

print("-" * 50)
print(f"Passed: {passed}/{len(test_queries)}")
