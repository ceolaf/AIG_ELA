#!/usr/bin/env python3
"""
Parse AIG result files into individual item files with CSV metadata tracking.
"""

import os
import re
import csv
from datetime import datetime
from typing import Optional, List, Tuple
import random


def select_standard_folder() -> Optional[str]:
    """
    Prompt user to select a standard folder matching the pattern.
    Returns the folder name or None.
    """
    pattern = re.compile(r"^ ?R[LI][ .]?(?:\d|9-10|11-12)\.\d+$", re.IGNORECASE)
    
    candidates = []
    for name in os.listdir("."):
        if os.path.isdir(name) and pattern.fullmatch(name):
            candidates.append(name)
    
    candidates.sort()
    
    if not candidates:
        print("\nNo standard directories found matching pattern.")
        return None
    
    print("\n" + "=" * 50)
    print("   Select a Standard Folder")
    print("=" * 50)
    for idx, name in enumerate(candidates, start=1):
        print(f"  {idx}) {name}")
    print("=" * 50)
    
    while True:
        choice = input(f"Enter your choice (1-{len(candidates)}): ").strip()
        if not choice.isdigit():
            print("Please enter a number.")
            continue
        
        index = int(choice)
        if 1 <= index <= len(candidates):
            return candidates[index - 1]
        
        print(f"Please enter a number between 1 and {len(candidates)}.")


def find_results_folder(standard_folder: str) -> Optional[str]:
    """
    Find the Results folder inside the standard folder.
    Returns the folder path or None.
    """
    candidates = []
    for name in os.listdir(standard_folder):
        full_path = os.path.join(standard_folder, name)
        if os.path.isdir(full_path) and "result" in name.lower():
            candidates.append(name)
    
    if not candidates:
        print(f"\nNo Results folder found in {standard_folder}")
        return None
    
    if len(candidates) == 1:
        print(f"\nUsing Results folder: {candidates[0]}")
        return os.path.join(standard_folder, candidates[0])
    
    print("\n" + "=" * 50)
    print("   Select a Results Folder")
    print("=" * 50)
    for idx, name in enumerate(candidates, start=1):
        print(f"  {idx}) {name}")
    print("=" * 50)
    
    while True:
        choice = input(f"Enter your choice (1-{len(candidates)}): ").strip()
        if not choice.isdigit():
            print("Please enter a number.")
            continue
        
        index = int(choice)
        if 1 <= index <= len(candidates):
            return os.path.join(standard_folder, candidates[index - 1])
        
        print(f"Please enter a number between 1 and {len(candidates)}.")


def generate_unique_random(used_numbers: set) -> str:
    """Generate a unique 5-digit random number."""
    while True:
        num = random.randint(10000, 99999)
        if num not in used_numbers:
            used_numbers.add(num)
            return str(num)


def parse_metadata_line(line: str) -> dict:
    """
    Parse a line like "Tier 7b (GPT) #1 (temp=0.7). (6.44 secs). (5352 + 448 = 5800 total tokens)"
    Returns a dict with all available metadata.
    """
    metadata = {
        'tier': '',
        'llm': '',
        'iteration': '',
        'temperature': '',
        'elapsed_time': '',
        'input_tokens': '',
        'output_tokens': '',
        'total_tokens': ''
    }
    
    # Extract tier
    tier_match = re.search(r'Tier\s+(\w+)', line)
    if tier_match:
        metadata['tier'] = tier_match.group(1)
    
    # Extract LLM (in parentheses)
    llm_match = re.search(r'\(([^)]+)\)\s*#', line)
    if llm_match:
        metadata['llm'] = llm_match.group(1)
    
    # Extract iteration number
    iter_match = re.search(r'#(\d+)', line)
    if iter_match:
        metadata['iteration'] = iter_match.group(1)
    
    # Extract temperature
    temp_match = re.search(r'temp=([\d.]+)', line)
    if temp_match:
        metadata['temperature'] = temp_match.group(1)
    
    # Extract elapsed time
    time_match = re.search(r'\(([\d.]+)\s*secs?\)', line)
    if time_match:
        metadata['elapsed_time'] = time_match.group(1)
    
    # Extract tokens: (input + output = total total tokens)
    tokens_match = re.search(r'\((\d+)\s*\+\s*(\d+)\s*=\s*(\d+)\s+total tokens\)', line)
    if tokens_match:
        metadata['input_tokens'] = tokens_match.group(1)
        metadata['output_tokens'] = tokens_match.group(2)
        metadata['total_tokens'] = tokens_match.group(3)
    
    return metadata


def parse_passage_line(line: str) -> str:
    """
    Extract passage name from a line like:
    "Passage: RL 8.1 The Night Circus (MA grade 8 2023 MCAS).txt"
    Returns the passage name (everything between standard and .txt)
    """
    if not line.startswith("Passage:"):
        return ""
    
    # Remove "Passage: " prefix
    content = line[8:].strip()
    
    # Remove .txt suffix if present
    if content.endswith(".txt"):
        content = content[:-4]
    
    # Remove the standard prefix (e.g., "RL 8.1 ")
    # Look for pattern like "RL 8.1" or "RI 7.3"
    standard_match = re.match(r'^R[LI][ .]?(?:\d|9-10|11-12)\.\d+\s+', content)
    if standard_match:
        content = content[len(standard_match.group(0)):]
    
    return content.strip()


def process_results_file(
    filepath: str,
    standard: str,
    output_dir: str,
    csv_writer,
    used_numbers: set
) -> int:
    """
    Process a single results file and extract all items.
    Returns the number of items processed.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by item separators (flexible number of =)
    items = re.split(r'\n={10,}\s+NEW ITEM\s+={10,}\n', content)
    
    item_count = 0
    
    for item_text in items:
        if not item_text.strip():
            continue
        
        lines = item_text.split('\n')
        
        # Find metadata line and passage line
        metadata = {}
        passage = ""
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for Tier line
            if 'Tier' in line and ('GPT' in line or 'Gemini' in line or 
                                   'Claude' in line or 'Copilot' in line):
                metadata = parse_metadata_line(line)
            
            # Look for Passage line
            if line.startswith("Passage:"):
                passage = parse_passage_line(line)
        
        # Skip if no metadata found
        if not metadata.get('tier'):
            continue
        
        item_count += 1
        
        # Generate unique filename
        random_num = generate_unique_random(used_numbers)
        if passage:
            filename = f"{standard} {random_num} {passage}.txt"
        else:
            filename = f"{standard} {random_num}.txt"
        
        filepath_out = os.path.join(output_dir, filename)
        
        # Write item file
        with open(filepath_out, 'w', encoding='utf-8') as f:
            f.write(f"Standard: {standard}\n")
            if passage:
                f.write(f"Passage: {passage}\n")
            f.write("\n" + "=" * 60 + "\n\n")
            f.write(item_text.strip())
        
        # Write CSV row
        csv_row = [
            filename,
            standard,
            passage,
            metadata.get('tier', ''),
            metadata.get('llm', ''),
            metadata.get('iteration', ''),
            metadata.get('temperature', ''),
            metadata.get('elapsed_time', ''),
            metadata.get('input_tokens', ''),
            metadata.get('output_tokens', ''),
            metadata.get('total_tokens', '')
        ]
        csv_writer.writerow(csv_row)
        
        # Display to screen
        print(f"Processed: {','.join(csv_row)}")
    
    return item_count


def main():
    # 1. Select standard folder
    standard = select_standard_folder()
    if not standard:
        return
    
    # 2. Find Results folder
    results_folder = find_results_folder(standard)
    if not results_folder:
        return
    
    # 3. Create output folder with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(standard, f"Individual Items {timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nCreated output folder: {output_dir}")
    
    # 4. Create CSV log file
    csv_filename = os.path.join(output_dir, "items_log.csv")
    csv_headers = [
        'Filename',
        'Standard',
        'Passage',
        'Tier',
        'LLM',
        'Iteration',
        'Temperature',
        'Elapsed Time (secs)',
        'Input Tokens',
        'Output Tokens',
        'Total Tokens'
    ]
    
    # Track used random numbers
    used_numbers = set()
    
    total_items = 0
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(csv_headers)
        
        # Process all .txt files in results folder
        for filename in os.listdir(results_folder):
            if filename.endswith('.txt'):
                filepath = os.path.join(results_folder, filename)
                print(f"\nProcessing: {filename}")
                count = process_results_file(
                    filepath,
                    standard,
                    output_dir,
                    csv_writer,
                    used_numbers
                )
                total_items += count
    
    print("\n" + "=" * 60)
    print(f"COMPLETE: Processed {total_items} items")
    print(f"Output folder: {output_dir}")
    print(f"CSV log: {csv_filename}")
    print("=" * 60)


if __name__ == "__main__":
    main()