#!/usr/bin/env python3
"""
Generate performance benchmark report from test results.

Creates a markdown report with graphs and analysis.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import statistics


class PerformanceReportGenerator:
    """Generate markdown reports from benchmark results."""
    
    def __init__(self, results_file: str):
        with open(results_file, 'r') as f:
            self.data = json.load(f)
        self.results = self.data["results"]
        self.summary = self.data["summary"]
        self.environment = self.data["test_environment"]
        
    def generate_report(self) -> str:
        """Generate complete performance report."""
        report = []
        
        # Header
        report.append("# Performance Benchmarks")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test Environment
        report.append("\n## Test Environment")
        report.append(f"- **Python Version**: {self.environment['python_version'].split()[0]}")
        report.append(f"- **Platform**: {self.environment['platform']}")
        report.append(f"- **CPU Cores**: {self.environment['cpu_count']}")
        report.append(f"- **Total Memory**: {self.environment['total_memory_gb']:.1f} GB")
        
        # Executive Summary
        report.append("\n## Executive Summary")
        report.extend(self._generate_executive_summary())
        
        # README Claims Validation
        report.append("\n## README Claims Validation")
        report.extend(self._validate_readme_claims())
        
        # Detailed Results
        report.append("\n## Detailed Results")
        
        # Search Performance
        report.append("\n### Search Performance")
        report.extend(self._analyze_search_performance())
        
        # Write Performance
        report.append("\n### Write Performance")
        report.extend(self._analyze_write_performance())
        
        # Weekly Summary Performance
        report.append("\n### Weekly Summary Performance")
        report.extend(self._analyze_summary_performance())
        
        # Performance Graphs (ASCII)
        report.append("\n## Performance Scaling")
        report.extend(self._generate_ascii_graphs())
        
        # Recommendations
        report.append("\n## Recommendations")
        report.extend(self._generate_recommendations())
        
        return "\n".join(report)
        
    def _generate_executive_summary(self) -> List[str]:
        """Generate executive summary of results."""
        lines = []
        
        # Find README validation result
        readme_results = [r for r in self.results if r["operation"] == "readme_claim_validation"]
        if readme_results:
            result = readme_results[0]
            if "additional_info" in result and result["additional_info"].get("claim_met", False):
                lines.append(f"✅ **README claim validated**: Search completes in {result['duration_seconds']:.2f}s (< 5s) with {result['dataset_size']} conversations")
            else:
                duration = result.get('duration_seconds', 0)
                size = result.get('dataset_size', 159)
                if duration < 5.0:
                    lines.append(f"✅ **README claim validated**: Search completes in {duration:.2f}s (< 5s) with {size} conversations")
                else:
                    lines.append(f"❌ **README claim failed**: Search took {duration:.2f}s (> 5s) with {size} conversations")
                
        # Overall performance summary
        search_results = self.summary.get("search_single_common_keyword", {})
        if 159 in search_results:
            avg_search = search_results[159]["avg_duration"]
            lines.append(f"- Average search time (159 conversations): **{avg_search:.3f}s**")
            
        # Memory usage
        memory_results = [r for r in self.results if "memory_leak_test" in r["operation"]]
        if memory_results and "additional_info" in memory_results[0]:
            memory_per_search = memory_results[0]["additional_info"].get("memory_per_search", 0)
            lines.append(f"- Memory usage per search: **{memory_per_search:.3f} MB**")
            
        return lines
        
    def _validate_readme_claims(self) -> List[str]:
        """Validate specific README claims."""
        lines = []
        
        lines.append("\n| Claim | Measured | Status | Notes |")
        lines.append("|-------|----------|---------|-------|")
        
        # Search performance claim
        search_159 = self._get_search_time_for_size(159)
        if search_159:
            status = "✅ PASS" if search_159 < 5.0 else "❌ FAIL"
            lines.append(f"| Sub-5 second search (159 conversations) | {search_159:.2f}s | {status} | Average across different query types |")
            
        # Dataset size claim
        stats_results = [r for r in self.results if r["operation"] == "readme_claim_validation"]
        if stats_results and "additional_info" in stats_results[0] and "total_size_mb" in stats_results[0]["additional_info"]:
            size_mb = stats_results[0]["additional_info"]["total_size_mb"]
            size_diff = abs(size_mb - 8.8)
            status = "✅ PASS" if size_diff < 1.0 else "⚠️ CLOSE" if size_diff < 2.0 else "❌ FAIL"
            lines.append(f"| 8.8MB for 159 conversations | {size_mb:.1f}MB | {status} | {size_diff:.1f}MB difference |")
            
        # Memory usage claim
        memory_results = self._get_peak_memory_usage()
        if memory_results:
            status = "✅ PASS" if memory_results < 100 else "❌ FAIL"
            lines.append(f"| Minimal RAM usage | {memory_results:.1f}MB peak | {status} | During search operations |")
            
        return lines
        
    def _analyze_search_performance(self) -> List[str]:
        """Analyze search performance results."""
        lines = []
        
        # Create table of search performance by dataset size
        lines.append("\n#### Search Time by Dataset Size")
        lines.append("\n| Dataset Size | Avg Time (s) | Min Time (s) | Max Time (s) | Samples |")
        lines.append("|--------------|--------------|--------------|--------------|----------|")
        
        # Get all search operations
        search_ops = [op for op in self.summary.keys() if op.startswith("search_")]
        
        # Aggregate by dataset size
        size_data = {}
        for op in search_ops:
            for size, stats in self.summary[op].items():
                if size not in size_data:
                    size_data[size] = []
                size_data[size].append(stats)
                
        # Generate table rows
        for size in sorted(size_data.keys()):
            all_stats = size_data[size]
            avg_times = [s["avg_duration"] for s in all_stats]
            min_times = [s["min_duration"] for s in all_stats]
            max_times = [s["max_duration"] for s in all_stats]
            
            overall_avg = statistics.mean(avg_times)
            overall_min = min(min_times)
            overall_max = max(max_times)
            total_samples = sum(s["sample_count"] for s in all_stats)
            
            lines.append(f"| {size} | {overall_avg:.3f} | {overall_min:.3f} | {overall_max:.3f} | {total_samples} |")
            
        # Query type analysis
        lines.append("\n#### Search Performance by Query Type")
        lines.append("\n| Query Type | 159 Convs Time (s) | Scaling Factor* |")
        lines.append("|------------|-------------------|------------------|")
        
        for op in sorted(search_ops):
            query_type = op.replace("search_", "").replace("_", " ").title()
            
            # Get time for 159 conversations
            if 159 in self.summary[op]:
                time_159 = self.summary[op][159]["avg_duration"]
                
                # Calculate scaling factor (time per 100 conversations)
                scaling = (time_159 / 159) * 100
                
                lines.append(f"| {query_type} | {time_159:.3f} | {scaling:.3f}s/100 |")
                
        lines.append("\n*Scaling Factor: Estimated time per 100 conversations")
        
        return lines
        
    def _analyze_write_performance(self) -> List[str]:
        """Analyze write performance results."""
        lines = []
        
        write_ops = [op for op in self.summary.keys() if op.startswith("add_conversation")]
        
        if write_ops:
            lines.append("\n| Content Size | Avg Time (s) | Throughput (KB/s) |")
            lines.append("|--------------|--------------|-------------------|")
            
            for op in sorted(write_ops):
                size_name = op.replace("add_conversation_", "")
                
                # Get the first (and likely only) size entry
                for size_bytes, stats in self.summary[op].items():
                    avg_time = stats["avg_duration"]
                    # Convert size_bytes to int if it's a string
                    size_kb = int(size_bytes) / 1024 if isinstance(size_bytes, str) else size_bytes / 1024
                    throughput = size_kb / avg_time if avg_time > 0 else 0
                    
                    lines.append(f"| {size_name} | {avg_time:.3f} | {throughput:.1f} |")
                    
        return lines
        
    def _analyze_summary_performance(self) -> List[str]:
        """Analyze weekly summary performance."""
        lines = []
        
        summary_ops = [op for op in self.summary.keys() if "weekly_summary" in op]
        
        if summary_ops:
            lines.append("\n| Week Size | Generation Time (s) |")
            lines.append("|-----------|-------------------|")
            
            for op in summary_ops:
                for size, stats in sorted(self.summary[op].items()):
                    lines.append(f"| {size} conversations | {stats['avg_duration']:.3f} |")
                    
        return lines
        
    def _generate_ascii_graphs(self) -> List[str]:
        """Generate ASCII graphs showing performance scaling."""
        lines = []
        
        # Search performance scaling graph
        lines.append("\n### Search Time vs Dataset Size")
        lines.append("```")
        lines.extend(self._create_ascii_graph("search", "Dataset Size", "Time (s)"))
        lines.append("```")
        
        return lines
        
    def _create_ascii_graph(self, operation_prefix: str, x_label: str, y_label: str) -> List[str]:
        """Create simple ASCII graph."""
        lines = []
        
        # Collect data points
        data_points = []
        for op in self.summary:
            if op.startswith(operation_prefix):
                for size, stats in self.summary[op].items():
                    data_points.append((size, stats["avg_duration"]))
                    
        if not data_points:
            return ["No data available"]
            
        # Sort by size
        data_points.sort()
        
        # Simple bar chart
        max_time = max(time for _, time in data_points)
        scale = 50 / max_time if max_time > 0 else 1
        
        lines.append(f"{y_label}")
        lines.append("│")
        
        for size, time in data_points:
            bar_length = int(time * scale)
            bar = "█" * bar_length
            lines.append(f"{time:5.2f}s │{bar} {size}")
            
        lines.append(f"       └{'─' * 52}")
        lines.append(f"         {x_label}")
        
        return lines
        
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations."""
        lines = []
        
        # Check if performance meets expectations
        search_159 = self._get_search_time_for_size(159)
        
        if search_159 and search_159 < 5.0:
            lines.append("✅ **Current performance is acceptable** for the intended use case (personal conversation storage)")
            lines.append("\n### Optimization Opportunities (Optional)")
        else:
            lines.append("⚠️ **Performance optimization recommended**")
            lines.append("\n### Suggested Optimizations (Priority Order)")
            
        # Always include optimization suggestions
        lines.extend([
            "\n1. **Implement Search Caching**",
            "   - Cache recent search results (LRU cache)",
            "   - Invalidate on new conversation additions",
            "   - Expected improvement: 50-90% for repeated searches",
            "",
            "2. **Add Search Index**",
            "   - Create inverted index for common terms",
            "   - Update index on conversation additions",
            "   - Expected improvement: 70-80% for large datasets",
            "",
            "3. **Migrate to SQLite FTS** (for > 500 conversations)",
            "   - Full-text search with built-in indexing",
            "   - Better memory efficiency",
            "   - Expected improvement: 90% for large datasets",
            "",
            "4. **Optimize File I/O**",
            "   - Batch file reads where possible",
            "   - Use memory-mapped files for large datasets",
            "   - Expected improvement: 20-30%"
        ])
        
        # Performance monitoring
        lines.extend([
            "\n### Performance Monitoring",
            "- Set up automated benchmarks in CI/CD",
            "- Monitor performance regression (> 10% threshold)",
            "- Track real-world usage patterns",
            "- Review optimization needs at 1000+ conversations"
        ])
        
        return lines
        
    def _get_search_time_for_size(self, size: int) -> float:
        """Get average search time for a specific dataset size."""
        times = []
        for op in self.summary:
            if op.startswith("search_") and size in self.summary[op]:
                times.append(self.summary[op][size]["avg_duration"])
        return statistics.mean(times) if times else None
        
    def _get_peak_memory_usage(self) -> float:
        """Get peak memory usage across all operations."""
        peak_memory = 0
        for result in self.results:
            if "peak_memory_mb" in result:
                peak_memory = max(peak_memory, result["peak_memory_mb"])
        return peak_memory


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate performance report from benchmark results")
    parser.add_argument("results_file", help="Path to benchmark results JSON file")
    parser.add_argument("--output", "-o", help="Output file path (default: docs/PERFORMANCE_BENCHMARKS.md)")
    
    args = parser.parse_args()
    
    # Generate report
    generator = PerformanceReportGenerator(args.results_file)
    report = generator.generate_report()
    
    # Save report
    output_path = args.output or "docs/PERFORMANCE_BENCHMARKS.md"
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(report)
        
    print(f"Performance report generated: {output_file}")
    
    # Also print summary to console
    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)
    
    # Extract key metrics
    with open(args.results_file, 'r') as f:
        data = json.load(f)
        
    # README claim validation
    readme_results = [r for r in data["results"] if r["operation"] == "readme_claim_validation"]
    if readme_results:
        result = readme_results[0]
        actual_time = result.get("duration_seconds", 0)
        
        if "additional_info" in result:
            claim_met = result["additional_info"].get("claim_met", actual_time < 5.0)
        else:
            claim_met = actual_time < 5.0
        
        if claim_met:
            print(f"✅ README claim PASSED: {actual_time:.2f}s < 5s")
        else:
            print(f"❌ README claim FAILED: {actual_time:.2f}s > 5s")


if __name__ == "__main__":
    main()