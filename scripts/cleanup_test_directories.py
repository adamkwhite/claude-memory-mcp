#!/usr/bin/env python3
"""
Repository cleanup script for test directories

This script removes test directories and files that were accidentally 
committed to the repository root. It includes safety checks and 
dry-run functionality.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Set
import argparse


def get_git_deleted_files() -> List[str]:
    """Get list of deleted files from git status."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'], 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        deleted_files = []
        for line in result.stdout.strip().split('\n'):
            if line.startswith(' D '):
                deleted_files.append(line[3:])  # Remove ' D ' prefix
        
        return deleted_files
    except subprocess.CalledProcessError as e:
        print(f"Error running git status: {e}")
        return []


def extract_test_directories(file_paths: List[str]) -> Set[str]:
    """Extract unique test directory names from file paths."""
    test_dirs = set()
    
    for file_path in file_paths:
        parts = Path(file_path).parts
        
        # Look for test directory patterns in the first part (root level)
        if parts and len(parts) > 0:
            first_part = parts[0]
            
            # Check if it matches test directory patterns
            if (first_part.startswith('test_') or 
                first_part.startswith('claude_memory_test_') or
                '_test_' in first_part or
                first_part == 'None' or
                first_part.endswith('_test')):
                test_dirs.add(first_part)
    
    return test_dirs


def remove_test_directories(test_dirs: Set[str], dry_run: bool = True) -> None:
    """Remove test directories with safety checks."""
    project_root = Path(__file__).parent.parent
    
    if not test_dirs:
        print("No test directories found to remove.")
        return
    
    print(f"\n{'DRY RUN: ' if dry_run else ''}Found {len(test_dirs)} test directories to remove:")
    for directory in sorted(test_dirs):
        dir_path = project_root / directory
        if dir_path.exists():
            file_count = len(list(dir_path.rglob('*'))) if dir_path.is_dir() else 1
            print(f"  - {directory}/ ({file_count} files)")
        else:
            print(f"  - {directory}/ (already removed)")
    
    if dry_run:
        print(f"\nDRY RUN: Would remove {len(test_dirs)} directories.")
        print("Add --execute flag to perform actual removal.")
        return
    
    # Get user confirmation in interactive mode
    if sys.stdin.isatty():
        try:
            response = input(f"\nRemove {len(test_dirs)} test directories? (y/N): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
        except EOFError:
            # Non-interactive environment, proceed with removal
            print("Non-interactive environment detected, proceeding with removal...")
    
    # Remove directories
    removed_count = 0
    for directory in test_dirs:
        dir_path = project_root / directory
        
        try:
            if dir_path.exists() and dir_path.is_dir():
                shutil.rmtree(dir_path)
                print(f"Removed: {directory}/")
                removed_count += 1
            elif dir_path.exists():
                dir_path.unlink()
                print(f"Removed file: {directory}")
                removed_count += 1
        except Exception as e:
            print(f"Error removing {directory}: {e}")
    
    print(f"\nSuccessfully removed {removed_count} test directories.")


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description='Clean up test directories from repository root')
    parser.add_argument('--execute', action='store_true', 
                       help='Execute the cleanup (default is dry-run)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    print("Repository Test Directory Cleanup")
    print("=" * 40)
    
    # Get deleted files from git status
    deleted_files = get_git_deleted_files()
    
    if args.verbose:
        print(f"Found {len(deleted_files)} deleted files in git status")
    
    # Extract test directories
    test_dirs = extract_test_directories(deleted_files)
    
    # Also check for existing test directories in current directory
    project_root = Path(__file__).parent.parent
    existing_test_dirs = set()
    
    for item in project_root.iterdir():
        if item.is_dir():
            name = item.name
            if (name.startswith('test_') or 
                name.startswith('claude_memory_test_') or
                '_test_' in name or
                name == 'None' or
                name.endswith('_test')):
                # Exclude legitimate directories
                if name not in ['tests', '.pytest_cache']:
                    existing_test_dirs.add(name)
    
    all_test_dirs = test_dirs.union(existing_test_dirs)
    
    if args.verbose:
        print(f"Test directories from git: {sorted(test_dirs)}")
        print(f"Existing test directories: {sorted(existing_test_dirs)}")
    
    # Remove test directories
    remove_test_directories(all_test_dirs, dry_run=not args.execute)


if __name__ == '__main__':
    main()