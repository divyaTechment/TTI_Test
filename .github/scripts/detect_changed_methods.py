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
        
        # Extract methods from the file
        methods = extract_methods_from_file(file_path)
        
        if not methods:
            continue
        
        # Check git diff to see which specific methods changed
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD~1", "HEAD", "--", file_path],
                capture_output=True,
                text=True,
                check=True
            )
            diff_content = result.stdout
            
            if not diff_content.strip():
                # No diff found, try comparing with origin
                try:
                    result = subprocess.run(
                        ["git", "diff", "origin/main...HEAD", "--", file_path],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    diff_content = result.stdout
                except subprocess.CalledProcessError:
                    diff_content = ""
            
            # Find methods that appear in the diff (added/modified lines)
            detected_methods = []
            for method in methods:
                # Check if method definition appears in diff (look for def method_name)
                # Also check for method body changes (lines inside the method)
                method_pattern = rf'def\s+{method}\s*\('
                if re.search(method_pattern, diff_content):
                    # Format: app/calculator.add (with slash, not dot)
                    # This matches the @pytest.mark.impact("app/calculator.add") format
                    method_path = f"{file_path.replace('.py', '').replace('\\', '/')}.{method}"
                    detected_methods.append(method_path)
            
            if detected_methods:
                # Specific methods detected
                changed_methods.extend(detected_methods)
            else:
                # No specific methods detected, include all methods from changed file
                # This ensures tests run when file is changed but we can't detect specific methods
                for method in methods:
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
        # Remove duplicates and sort
        unique_methods = sorted(list(set(changed_methods)))
        output = ",".join(unique_methods)
        print(output, end="")
        # Debug output to stderr (won't affect the output)
        print(f"DEBUG: Detected {len(unique_methods)} changed methods: {output}", file=sys.stderr)
    else:
        # If no methods found at all, output empty (will run all tests)
        print("", end="")
        print("DEBUG: No methods detected, will run all tests", file=sys.stderr)


if __name__ == "__main__":
    main()

