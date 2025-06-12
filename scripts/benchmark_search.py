#!/usr/bin/env python3
"""
Search Performance Benchmark Suite

This script creates comprehensive benchmarks for the current search implementation
to establish baseline metrics before migrating to SQLite FTS.

Usage:
    python scripts/benchmark_search.py --dataset small
    python scripts/benchmark_search.py --dataset medium --output benchmark_results.json
    python scripts/benchmark_search.py --dataset large --iterations 5
"""

import argparse
import json
import time
import os
import statistics
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Optional psutil import for memory monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available, memory monitoring will be limited")

# Add project root to path for imports
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from src.conversation_memory import ConversationMemoryServer


class SearchBenchmark:
    """Comprehensive search performance benchmark suite"""
    
    def __init__(self, storage_path: str = None):
        """Initialize benchmark with test storage path"""
        if storage_path is None:
            storage_path = project_root / "benchmark_data"
        
        self.storage_path = Path(storage_path)
        self.server = ConversationMemoryServer(str(self.storage_path))
        self.results = []
        
    def create_test_dataset(self, size: str) -> Dict[str, int]:
        """Create test conversation dataset of specified size"""
        dataset_configs = {
            "small": {"count": 100, "min_size": 1000, "max_size": 5000},
            "medium": {"count": 500, "min_size": 2000, "max_size": 10000},
            "large": {"count": 2000, "min_size": 1000, "max_size": 20000}
        }
        
        if size not in dataset_configs:
            raise ValueError(f"Dataset size must be one of: {list(dataset_configs.keys())}")
        
        config = dataset_configs[size]
        print(f"Creating {size} dataset with {config['count']} conversations...")
        
        # Sample conversation content templates
        templates = [
            "Discussion about Python programming and web development. Topics include Django framework, REST APIs, database optimization, and deployment strategies.",
            "Analysis of machine learning algorithms including neural networks, decision trees, and clustering techniques. Exploring scikit-learn and TensorFlow implementations.",
            "Code review session covering best practices, design patterns, and security considerations. Focus on maintainable and scalable software architecture.",
            "Troubleshooting session for debugging complex software issues. Investigating performance bottlenecks and memory leaks in production systems.",
            "System design discussion covering microservices, load balancing, caching strategies, and database sharding for high-traffic applications."
        ]
        
        topics_pool = [
            ["python", "programming", "web development"],
            ["machine learning", "neural networks", "data science"],
            ["code review", "best practices", "security"],
            ["debugging", "performance", "optimization"],
            ["system design", "microservices", "scalability"]
        ]
        
        created_count = 0
        for i in range(config['count']):
            template_idx = i % len(templates)
            base_content = templates[template_idx]
            
            # Pad content to reach target size
            target_size = config['min_size'] + (i * (config['max_size'] - config['min_size']) // config['count'])
            content = base_content
            while len(content) < target_size:
                content += f" Additional content for conversation {i} with technical details and examples. "
                content += "This includes code snippets, configuration examples, and detailed explanations. "
            
            title = f"Conversation {i+1}: {templates[template_idx][:50]}..."
            date = f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}T{(i % 24):02d}:00:00Z"
            
            result = self.server.add_conversation(
                content=content,
                title=title,
                conversation_date=date
            )
            
            if result.get("status") == "success":
                created_count += 1
            
            if (i + 1) % 100 == 0:
                print(f"  Created {i + 1}/{config['count']} conversations...")
        
        print(f"Dataset creation complete: {created_count} conversations created")
        return {
            "total_conversations": created_count,
            "avg_size": (config['min_size'] + config['max_size']) // 2,
            "size_range": f"{config['min_size']}-{config['max_size']} chars"
        }
    
    def measure_memory_usage(self) -> Dict[str, float]:
        """Measure current memory usage"""
        if PSUTIL_AVAILABLE:
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
                "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            }
        else:
            # Fallback to basic memory monitoring using /proc/self/status
            try:
                with open('/proc/self/status', 'r') as f:
                    for line in f:
                        if line.startswith('VmRSS:'):
                            rss_kb = int(line.split()[1])
                            return {
                                "rss_mb": rss_kb / 1024,
                                "vms_mb": rss_kb / 1024,  # Approximate
                            }
                return {"rss_mb": 0.0, "vms_mb": 0.0}
            except (OSError, ValueError):
                return {"rss_mb": 0.0, "vms_mb": 0.0}
    
    def benchmark_search_query(self, query: str, limit: int = 10, iterations: int = 3) -> Dict[str, Any]:
        """Benchmark a single search query with multiple iterations"""
        print(f"    Benchmarking query: '{query}' (limit={limit})")
        
        times = []
        memory_before = []
        memory_after = []
        result_counts = []
        
        for i in range(iterations):
            # Measure memory before
            mem_before = self.measure_memory_usage()
            memory_before.append(mem_before['rss_mb'])
            
            # Time the search operation
            start_time = time.perf_counter()
            results = self.server.search_conversations(query, limit)
            end_time = time.perf_counter()
            
            # Measure memory after
            mem_after = self.measure_memory_usage()
            memory_after.append(mem_after['rss_mb'])
            
            search_time = end_time - start_time
            times.append(search_time)
            result_counts.append(len(results))
            
            # Small delay between iterations
            time.sleep(0.1)
        
        return {
            "query": query,
            "limit": limit,
            "iterations": iterations,
            "times": {
                "min": min(times),
                "max": max(times),
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "stdev": statistics.stdev(times) if len(times) > 1 else 0.0
            },
            "memory_usage_mb": {
                "before_mean": statistics.mean(memory_before),
                "after_mean": statistics.mean(memory_after),
                "increase_mean": statistics.mean([after - before for before, after in zip(memory_before, memory_after)])
            },
            "result_count": {
                "min": min(result_counts),
                "max": max(result_counts),
                "mean": statistics.mean(result_counts)
            }
        }
    
    def run_comprehensive_benchmark(self, iterations: int = 3) -> Dict[str, Any]:
        """Run comprehensive benchmark suite"""
        print("Starting comprehensive search benchmark...")
        
        # Test queries of varying complexity and expected result counts
        test_queries = [
            # Common/broad queries (high result count)
            ("python", 20),
            ("programming", 15),
            ("machine learning", 10),
            
            # Specific queries (medium result count)
            ("django framework", 10),
            ("neural networks", 10),
            ("code review", 10),
            
            # Specific/narrow queries (low result count)
            ("TensorFlow implementations", 5),
            ("microservices architecture", 5),
            ("performance optimization", 5),
            
            # Very specific queries (very low result count)
            ("database sharding", 5),
            ("memory leaks production", 3),
            ("scalability best practices", 3)
        ]
        
        benchmark_results = []
        overall_start = time.perf_counter()
        
        for query, limit in test_queries:
            result = self.benchmark_search_query(query, limit, iterations)
            benchmark_results.append(result)
        
        overall_end = time.perf_counter()
        
        # Calculate aggregate statistics
        all_times = []
        all_memory_increases = []
        total_results = 0
        
        for result in benchmark_results:
            all_times.extend([result['times']['mean']])
            all_memory_increases.append(result['memory_usage_mb']['increase_mean'])
            total_results += result['result_count']['mean']
        
        aggregate_stats = {
            "total_benchmark_time": overall_end - overall_start,
            "queries_tested": len(test_queries),
            "total_iterations": len(test_queries) * iterations,
            "search_time_stats": {
                "min": min(all_times),
                "max": max(all_times),
                "mean": statistics.mean(all_times),
                "median": statistics.median(all_times),
                "stdev": statistics.stdev(all_times) if len(all_times) > 1 else 0.0
            },
            "memory_increase_stats": {
                "mean": statistics.mean(all_memory_increases),
                "max": max(all_memory_increases),
                "total_results_returned": total_results
            }
        }
        
        return {
            "benchmark_timestamp": datetime.now().isoformat(),
            "individual_queries": benchmark_results,
            "aggregate_statistics": aggregate_stats
        }
    
    def analyze_file_io_overhead(self) -> Dict[str, Any]:
        """Analyze file I/O overhead in current search implementation"""
        print("Analyzing file I/O overhead...")
        
        # Count total conversation files
        conversations_path = self.storage_path / "conversations"
        file_count = 0
        total_size = 0
        
        for year_dir in conversations_path.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                for month_dir in year_dir.iterdir():
                    if month_dir.is_dir():
                        for conv_file in month_dir.glob("*.json"):
                            file_count += 1
                            total_size += conv_file.stat().st_size
        
        avg_file_size = total_size / file_count if file_count > 0 else 0
        
        # Estimate I/O overhead per search
        estimated_io_time_per_file = 0.001  # 1ms per file (conservative estimate)
        estimated_total_io_time = file_count * estimated_io_time_per_file
        
        return {
            "total_files": file_count,
            "total_size_mb": total_size / 1024 / 1024,
            "average_file_size_kb": avg_file_size / 1024,
            "estimated_io_overhead": {
                "files_read_per_search": file_count,
                "estimated_time_per_file_ms": estimated_io_time_per_file * 1000,
                "estimated_total_io_time_ms": estimated_total_io_time * 1000,
                "percentage_of_search_time": "Measured in benchmark results"
            }
        }


def main():
    """Main benchmark execution"""
    parser = argparse.ArgumentParser(description="Search Performance Benchmark Suite")
    parser.add_argument(
        "--dataset", 
        choices=["small", "medium", "large"], 
        default="small",
        help="Dataset size for benchmarking"
    )
    parser.add_argument(
        "--iterations", 
        type=int, 
        default=3,
        help="Number of iterations per query"
    )
    parser.add_argument(
        "--output", 
        type=str,
        help="Output file for benchmark results (JSON format)"
    )
    parser.add_argument(
        "--create-dataset",
        action="store_true",
        help="Create new test dataset (will overwrite existing)"
    )
    parser.add_argument(
        "--storage-path",
        type=str,
        help="Custom storage path for benchmark data"
    )
    
    args = parser.parse_args()
    
    # Initialize benchmark
    benchmark = SearchBenchmark(args.storage_path)
    
    print(f"Search Performance Benchmark Suite")
    print(f"Dataset: {args.dataset}")
    print(f"Iterations per query: {args.iterations}")
    print(f"Storage path: {benchmark.storage_path}")
    print("-" * 50)
    
    try:
        # Create dataset if requested or if it doesn't exist
        if args.create_dataset or not (benchmark.storage_path / "conversations" / "index.json").exists():
            dataset_info = benchmark.create_test_dataset(args.dataset)
            print(f"Created dataset: {dataset_info}")
            print("-" * 50)
        
        # Run file I/O analysis
        io_analysis = benchmark.analyze_file_io_overhead()
        print(f"File I/O Analysis:")
        print(f"  Total files: {io_analysis['total_files']}")
        print(f"  Total size: {io_analysis['total_size_mb']:.2f} MB")
        print(f"  Average file size: {io_analysis['average_file_size_kb']:.2f} KB")
        print(f"  Files read per search: {io_analysis['estimated_io_overhead']['files_read_per_search']}")
        print("-" * 50)
        
        # Run comprehensive benchmark
        results = benchmark.run_comprehensive_benchmark(args.iterations)
        
        # Add I/O analysis to results
        results["file_io_analysis"] = io_analysis
        results["dataset_size"] = args.dataset
        results["storage_path"] = str(benchmark.storage_path)
        
        # Display summary results
        stats = results["aggregate_statistics"]
        print(f"\nBenchmark Results Summary:")
        print(f"  Total benchmark time: {stats['total_benchmark_time']:.2f}s")
        print(f"  Queries tested: {stats['queries_tested']}")
        print(f"  Average search time: {stats['search_time_stats']['mean']:.3f}s")
        print(f"  Search time range: {stats['search_time_stats']['min']:.3f}s - {stats['search_time_stats']['max']:.3f}s")
        print(f"  Average memory increase: {stats['memory_increase_stats']['mean']:.2f} MB")
        print(f"  Total results returned: {stats['memory_increase_stats']['total_results_returned']:.0f}")
        
        # Save results if output file specified
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nDetailed results saved to: {output_path}")
        
        print("\nBenchmark completed successfully!")
        
    except Exception as e:
        print(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())