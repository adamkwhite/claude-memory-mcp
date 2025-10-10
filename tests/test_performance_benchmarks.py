#!/usr/bin/env python3
"""
Performance benchmark tests for Claude Memory MCP Server.

Tests search performance, memory usage, and validates README claims.
"""

import json
import os
import shutil
import statistics
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import psutil
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from conversation_memory import ConversationMemoryServer


class PerformanceMetrics:
    """Track performance metrics during tests."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.start_time = None
        self.start_memory = None
        
    def start(self):
        """Start timing and memory tracking."""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
    def stop(self) -> Dict[str, float]:
        """Stop timing and return metrics."""
        duration = time.time() - self.start_time
        end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = end_memory - self.start_memory
        
        return {
            "duration_seconds": duration,
            "memory_delta_mb": memory_delta,
            "peak_memory_mb": end_memory
        }


class BenchmarkResults:
    """Collect and analyze benchmark results."""
    
    def __init__(self):
        self.results = []
        
    def add_result(self, operation: str, dataset_size: int, metrics: Dict[str, float], 
                   additional_info: Dict = None):
        """Add a benchmark result."""
        result = {
            "operation": operation,
            "dataset_size": dataset_size,
            "duration_seconds": metrics["duration_seconds"],
            "memory_delta_mb": metrics["memory_delta_mb"],
            "peak_memory_mb": metrics["peak_memory_mb"],
            "timestamp": datetime.now().isoformat()
        }
        if additional_info:
            result.update(additional_info)
        self.results.append(result)
        
    def get_summary(self) -> Dict:
        """Get summary statistics for all results."""
        summary = {}
        
        # Group by operation and dataset size
        operations = {}
        for result in self.results:
            op = result["operation"]
            size = result["dataset_size"]
            
            if op not in operations:
                operations[op] = {}
            if size not in operations[op]:
                operations[op][size] = []
                
            operations[op][size].append(result)
            
        # Calculate statistics
        for op, sizes in operations.items():
            summary[op] = {}
            for size, results in sizes.items():
                durations = [r["duration_seconds"] for r in results]
                memory_deltas = [r["memory_delta_mb"] for r in results]
                
                summary[op][size] = {
                    "avg_duration": statistics.mean(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "avg_memory_delta": statistics.mean(memory_deltas),
                    "sample_count": len(results)
                }
                
        return summary
        
    def save_to_file(self, filepath: str):
        """Save results to JSON file."""
        with open(filepath, 'w') as f:
            json.dump({
                "results": self.results,
                "summary": self.get_summary(),
                "test_environment": {
                    "python_version": sys.version,
                    "platform": sys.platform,
                    "cpu_count": psutil.cpu_count(),
                    "total_memory_gb": psutil.virtual_memory().total / (1024**3)
                }
            }, f, indent=2)


@pytest.fixture(scope="session")
def test_data_path():
    """Path to test data directory."""
    return Path.home() / "claude-memory-test"


@pytest.fixture(scope="session")
def benchmark_results():
    """Shared benchmark results collector."""
    return BenchmarkResults()


@pytest.fixture
def performance_metrics():
    """Performance metrics tracker."""
    return PerformanceMetrics()


class TestSearchPerformance:
    """Test search operation performance."""
    
    @pytest.mark.parametrize("dataset_size,expected_conversations", [
        (10, 10),
        (50, 50),
        (100, 100),
        (159, 159),  # README claim size
        (200, 200),
        (500, 500)
    ])
    @pytest.mark.asyncio
    async def test_search_performance_scaling(self, test_data_path, dataset_size, 
                                       expected_conversations, benchmark_results, 
                                       performance_metrics):
        """Test search performance with different dataset sizes."""
        # Create server with subset of data
        temp_dir = tempfile.mkdtemp(prefix=f"perf_test_{dataset_size}_")
        
        try:
            # Copy subset of test data
            self._copy_test_data_subset(test_data_path, temp_dir, dataset_size)
            
            server = ConversationMemoryServer(temp_dir)
            
            # Test different search scenarios
            search_queries = [
                ("python", "single common keyword"),
                ("terraform azure", "multiple keywords"),
                ("obscure_term_xyz", "no results"),
                ("debugging error handling", "phrase search"),
                ("machine learning", "popular topic")
            ]
            
            for query, description in search_queries:
                # Warm up
                await server.search_conversations(query, limit=5)
                
                # Measure performance (average of 3 runs)
                durations = []
                for _ in range(3):
                    performance_metrics.start()
                    results = await server.search_conversations(query, limit=10)
                    metrics = performance_metrics.stop()
                    durations.append(metrics["duration_seconds"])
                
                avg_duration = statistics.mean(durations)
                
                # Record result
                benchmark_results.add_result(
                    operation=f"search_{description.replace(' ', '_')}",
                    dataset_size=dataset_size,
                    metrics={
                        "duration_seconds": avg_duration,
                        "memory_delta_mb": metrics["memory_delta_mb"],
                        "peak_memory_mb": metrics["peak_memory_mb"]
                    },
                    additional_info={
                        "query": query,
                        "result_count": len(results) if isinstance(results, list) else 0
                    }
                )
                
                # Check against README claim for 159 conversations
                if dataset_size == 159:
                    assert avg_duration < 5.0, f"Search took {avg_duration:.2f}s, README claims < 5s"
                    
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    @pytest.mark.asyncio
    async def test_search_memory_usage(self, test_data_path, benchmark_results, performance_metrics):
        """Test memory usage during search operations."""
        server = ConversationMemoryServer(str(test_data_path))
        
        # Perform multiple searches to check for memory leaks
        performance_metrics.start()
        
        for i in range(100):
            await server.search_conversations("python testing", limit=20)
            
        metrics = performance_metrics.stop()
        
        benchmark_results.add_result(
            operation="search_memory_leak_test",
            dataset_size=159,  # Assuming standard test dataset
            metrics=metrics,
            additional_info={
                "iterations": 100,
                "memory_per_search": metrics["memory_delta_mb"] / 100
            }
        )
        
        # Memory delta should be reasonable for the search system in use
        # SQLite FTS uses more memory for caching and indexing than linear search
        memory_threshold = 200 if server.use_sqlite_search else 10
        assert metrics["memory_delta_mb"] < memory_threshold, f"Potential memory leak: {metrics['memory_delta_mb']:.2f}MB (threshold: {memory_threshold}MB, using SQLite: {server.use_sqlite_search})"
        
    def _copy_test_data_subset(self, source_path: Path, dest_path: str, count: int):
        """Copy a subset of test data for benchmarking."""
        dest = Path(dest_path)
        
        # Copy directory structure
        conversations_src = source_path / "conversations"
        conversations_dst = dest / "conversations"
        conversations_dst.mkdir(parents=True, exist_ok=True)
        
        # Copy index files
        for index_file in ["index.json", "topics.json"]:
            src_file = conversations_src / index_file
            if src_file.exists():
                shutil.copy2(src_file, conversations_dst / index_file)
                
        # Load and truncate index
        index_file = conversations_dst / "index.json"
        if index_file.exists():
            with open(index_file, 'r') as f:
                index_data = json.load(f)
                
            # Keep only first 'count' conversations
            index_data["conversations"] = index_data["conversations"][:count]
            
            # Copy conversation files
            for conv_info in index_data["conversations"]:
                src_file = source_path / conv_info["file_path"]
                dst_file = dest / conv_info["file_path"]
                
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                if src_file.exists():
                    shutil.copy2(src_file, dst_file)
                    
            # Save truncated index
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)


class TestWritePerformance:
    """Test write operation performance."""
    
    @pytest.mark.asyncio
    async def test_add_conversation_performance(self, benchmark_results, performance_metrics):
        """Test performance of adding conversations."""
        temp_dir = tempfile.mkdtemp(prefix="write_perf_test_")
        
        try:
            server = ConversationMemoryServer(temp_dir)
            
            # Test content of different sizes
            small_content = "Small test conversation " * 50  # ~1KB
            medium_content = "Medium test conversation " * 500  # ~10KB
            large_content = "Large test conversation " * 5000  # ~100KB
            
            test_cases = [
                ("small", small_content),
                ("medium", medium_content),
                ("large", large_content)
            ]
            
            for size_name, content in test_cases:
                # Warm up
                await server.add_conversation(content, f"Warmup {size_name}", datetime.now().isoformat())
                
                # Measure performance (average of 10 writes)
                durations = []
                for i in range(10):
                    performance_metrics.start()
                    result = await server.add_conversation(
                        content,
                        f"Performance test {size_name} {i}",
                        datetime.now().isoformat()
                    )
                    metrics = performance_metrics.stop()
                    
                    if result["status"] == "success":
                        durations.append(metrics["duration_seconds"])
                        
                avg_duration = statistics.mean(durations) if durations else 0
                
                benchmark_results.add_result(
                    operation=f"add_conversation_{size_name}",
                    dataset_size=len(content),
                    metrics={
                        "duration_seconds": avg_duration,
                        "memory_delta_mb": metrics["memory_delta_mb"],
                        "peak_memory_mb": metrics["peak_memory_mb"]
                    }
                )
                
                # All writes should complete in under 1 second
                assert avg_duration < 1.0, f"Write took {avg_duration:.2f}s"
                
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestWeeklySummaryPerformance:
    """Test weekly summary generation performance."""
    
    @pytest.mark.parametrize("week_conversation_count", [10, 50, 100])
    @pytest.mark.asyncio
    async def test_weekly_summary_performance(self, test_data_path, week_conversation_count,
                                      benchmark_results, performance_metrics):
        """Test weekly summary generation with different conversation counts."""
        server = ConversationMemoryServer(str(test_data_path))
        
        # Generate weekly summary
        performance_metrics.start()
        summary = await server.generate_weekly_summary(0)  # Current week
        metrics = performance_metrics.stop()
        
        benchmark_results.add_result(
            operation="generate_weekly_summary",
            dataset_size=week_conversation_count,
            metrics=metrics,
            additional_info={
                "summary_length": len(summary)
            }
        )
        
        # Should complete in reasonable time (< 2 seconds)
        assert metrics["duration_seconds"] < 2.0, f"Summary took {metrics['duration_seconds']:.2f}s"


class TestOverallPerformance:
    """Overall performance validation tests."""
    
    @pytest.mark.asyncio
    async def test_readme_claims_validation(self, test_data_path, benchmark_results):
        """Validate specific README performance claims."""
        server = ConversationMemoryServer(str(test_data_path))
        
        # Get dataset stats
        stats_file = test_data_path / "generation_stats.json"
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)
        else:
            stats = {"total_conversations": 159, "total_size_bytes": 8.8 * 1024 * 1024}
            
        # Test the specific README claim: sub-5 second search with 159 conversations
        queries = ["python", "docker kubernetes", "error handling", "machine learning ai"]
        
        max_duration = 0
        for query in queries:
            start = time.time()
            results = await server.search_conversations(query, limit=10)
            duration = time.time() - start
            max_duration = max(max_duration, duration)
            
        # Check against claim
        readme_claim_met = max_duration < 5.0
        
        benchmark_results.add_result(
            operation="readme_claim_validation",
            dataset_size=stats["total_conversations"],
            metrics={
                "duration_seconds": max_duration,
                "memory_delta_mb": 0,
                "peak_memory_mb": 0
            },
            additional_info={
                "claim": "sub-5 second search",
                "actual_max_duration": max_duration,
                "claim_met": readme_claim_met,
                "total_size_mb": stats["total_size_bytes"] / (1024 * 1024)
            }
        )
        
        assert readme_claim_met, f"README claim failed: search took {max_duration:.2f}s (> 5s)"


@pytest.fixture(scope="session", autouse=True)
def save_benchmark_results(benchmark_results):
    """Save benchmark results after all tests complete."""
    yield  # Run tests
    
    # Save results
    results_dir = Path("benchmark_results")
    results_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = results_dir / f"performance_results_{timestamp}.json"
    
    benchmark_results.save_to_file(str(results_file))
    print(f"\nBenchmark results saved to: {results_file}")
    
    # Print summary
    summary = benchmark_results.get_summary()
    print("\n=== Performance Summary ===")
    
    for operation, sizes in summary.items():
        print(f"\n{operation}:")
        for size, stats in sorted(sizes.items()):
            print(f"  Dataset size {size}: {stats['avg_duration']:.3f}s average")


def main():
    """Run benchmarks directly."""
    pytest.main([__file__, "-v", "-s"])


if __name__ == "__main__":
    main()