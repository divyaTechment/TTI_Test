#!/usr/bin/env python3
"""
Script to detect changed methods from git diff.
Extracts method-level changes from Python files for test impact analysis.
"""
import subprocess
import sys
import re
from pathlib import Path


def get_changed_files():
    """Get list of changed files from git diff."""
    try:
        # Get changed files between current commit and previous commit
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return [f.strip() for f in result.stdout.split("\n") if f.strip()]
    except subprocess.CalledProcessError:
        # Fallback: try to get changed files from merge base
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "origin/main...HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            return [f.strip() for f in result.stdout.split("\n") if f.strip()]
        except subprocess.CalledProcessError:
            # If no previous commit, return empty list
            return []


def extract_methods_from_file(file_path):
    """Extract method/function names from a Python file."""
    methods = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Match function definitions: def function_name(...)
            pattern = r'^def\s+(\w+)\s*\([^)]*\)\s*:'
            for match in re.finditer(pattern, content, re.MULTILINE):
                methods.append(match.group(1))
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
    return methods


def get_changed_methods(changed_files):
    """Get changed methods from changed Python files."""
    changed_methods = []
    
    for file_path in changed_files:
        if not file_path.endswith('.py'):
            continue
        
        # Convert to module path format (e.g., app/calculator.py -> app/calculator)
        module_path = file_path.replace('.py', '').replace('/', '.').replace('\\', '.')
        
        # Extract methods from the file
        methods = extract_methods_from_file(file_path)
        
        # Also check git diff to see which specific methods changed
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD~1", "HEAD", "--", file_path],
                capture_output=True,
                text=True,
                check=True
            )
            diff_content = result.stdout
            
            # Find methods that appear in the diff (added/modified lines)
            for method in methods:
                # Check if method definition appears in diff
                if f"def {method}" in diff_content:
                    # Format: app/calculator.add (with slash, not dot)
                    # This matches the @pytest.mark.impact("app/calculator.add") format
                    method_path = f"{file_path.replace('.py', '').replace('\\', '/')}.{method}"
                    changed_methods.append(method_path)
        except subprocess.CalledProcessError:
            # If we can't get diff, include all methods from changed file
            for method in methods:
                method_path = f"{file_path.replace('.py', '').replace('\\', '/')}.{method}"
                changed_methods.append(method_path)
    
    return changed_methods

def main():
    """Main function to detect and output changed methods."""
    changed_files = get_changed_files()
    
    if not changed_files:
        print("", end="")
        return
    
    # Filter only Python files in app/ directory
    app_files = [f for f in changed_files if f.startswith('app/') and f.endswith('.py')]
    
    if not app_files:
        print("", end="")
        return
    
    changed_methods = get_changed_methods(app_files)
    
    # Output comma-separated list of changed methods
    if changed_methods:
        print(",".join(changed_methods))
    else:
        # If no specific methods detected, output file paths
        print(",".join([f.replace('.py', '').replace('/', '.') for f in app_files]))


if __name__ == "__main__":
    main()

