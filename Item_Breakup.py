import re
import random
import os
import csv
import hashlib
from datetime import datetime

def get_valid_standard_folders():
    """
    Finds standard folders and allows the user to select one, multiple (comma-separated), or all.
    Returns a LIST of folder names.
    """
    # Pattern: Allows optional leading space (e.g. " RL 8.1" or "RL 8.1")
    pattern = re.compile(r"^ ?R[LI][ .]?(?:\d|9-10|11-12)\.\d+$", re.IGNORECASE)
    folders = [f for f in os.listdir('.') if os.path.isdir(f) and pattern.match(f)]
    
    if not folders:
        print("No folders found matching the Standard pattern (e.g., 'RL 8.4').")
        return []
    
    print("\n" + "="*40)
    print("   Available Standard Folders")
    print("="*40)
    print("0. [PROCESS ALL FOLDERS]")
    for i, folder in enumerate(folders, 1):
        print(f"{i}. {folder}")
    print("="*40)
    
    choice_str = input("\nSelect folder numbers (comma-separated, e.g., '1, 3') or '0' for all: ").strip()
    
    selected_folders = []
    
    # Handle "All"
    if choice_str == '0' or choice_str.lower() == 'all':
        return folders

    # Handle comma-separated list
    try:
        parts = [p.strip() for p in choice_str.split(',')]
        for p in parts:
            if not p: continue # skip empty
            idx = int(p) - 1
            if 0 <= idx < len(folders):
                selected_folders.append(folders[idx])
            else:
                print(f"Warning: '{p}' is not a valid number. Skipping.")
    except ValueError:
        print("Invalid input format. Please enter numbers separated by commas.")
        return []

    return selected_folders

def get_results_file(base_folder):
    """
    Finds result files within a specific standard folder.
    """
    # Finds folders with 'result' anywhere in the name
    results_dirs = [d for d in os.listdir(base_folder) 
                    if os.path.isdir(os.path.join(base_folder, d)) and 'result' in d.lower()]
    
    if not results_dirs:
        print(f"   [Skipping {base_folder}: No 'Results' subfolder found]")
        return []
    
    # If multiple result folders, ask user (or default to first if we want full automation)
    if len(results_dirs) == 1:
        res_dir = results_dirs[0]
    else:
        print(f"\nMultiple Results folders found in {base_folder}:")
        for i, d in enumerate(results_dirs, 1):
            print(f"{i}. {d}")
        try:
            choice_str = input("Select a Results folder number: ")
            res_dir = results_dirs[int(choice_str) - 1]
        except (ValueError, IndexError):
            return []

    target_path = os.path.join(base_folder, res_dir)
    files = [f for f in os.listdir(target_path) if f.endswith('.txt')]
    
    if not files:
        print(f"   [Skipping {base_folder}: No .txt files in results folder]")
        return []
    
    return [os.path.join(target_path, f) for f in files]

def get_passage_text(passage_filename):
    """
    Attempts to locate the passage file in the 'Passages' directory
    and returns its content. Handles case-insensitivity and leading spaces 
    for the folder name.
    """
    # 1. Find the actual Passages folder (handling case/spaces)
    passages_dir = None
    for candidate in os.listdir('.'):
        if os.path.isdir(candidate) and candidate.strip().lower() == "passages":
            passages_dir = candidate
            break
            
    if not passages_dir:
        return "\n\n[Passage file could not be appended: 'Passages' directory not found.]"

    # 2. Try exact match first
    full_path = os.path.join(passages_dir, passage_filename)
    if os.path.exists(full_path):
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f"\n\n================== Passage Text =================\n\n{f.read()}"
        except Exception as e:
            return f"\n\n[Error reading passage file: {e}]"
            
    # 3. If exact match fails, try adding .txt if missing
    if not passage_filename.lower().endswith('.txt'):
        full_path_txt = os.path.join(passages_dir, passage_filename + ".txt")
        if os.path.exists(full_path_txt):
            try:
                with open(full_path_txt, 'r', encoding='utf-8') as f:
                    return f"\n\n================== Passage Text =================\n\n{f.read()}"
            except Exception as e:
                return f"\n\n[Error reading passage file: {e}]"

    return f"\n\n[Passage file '{passage_filename}' not found in '{passages_dir}/' directory.]"

def process_items():
    # 1. Get List of Standards
    selected_standards = get_valid_standard_folders()
    if not selected_standards:
        print("No standards selected. Exiting.")
        return

    # 2. Setup Folder Structure
    base_output_dir = "Individual Items"
    os.makedirs(base_output_dir, exist_ok=True) # Ensure 'Individual Items' exists
    
    # Create the timestamped subfolder for THIS run
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    run_folder_name = f"Items {timestamp_str}"
    run_output_dir = os.path.join(base_output_dir, run_folder_name)
    os.makedirs(run_output_dir, exist_ok=True)
    
    # 3. Load Existing Checksums to Prevent Duplicates
    seen_checksums = set()
    csv_filename = os.path.join(base_output_dir, "item_metadata_log.csv")
    
    if os.path.isfile(csv_filename):
        try:
            with open(csv_filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if "Checksum" in reader.fieldnames:
                    for row in reader:
                        if row["Checksum"]:
                            seen_checksums.add(row["Checksum"])
            print(f"Loaded {len(seen_checksums)} existing items from log to prevent duplicates.")
        except Exception as e:
            print(f"Warning: Could not read existing log for duplicates ({e})")

    print(f"\nProcessing {len(selected_standards)} folders...")
    print(f"Saving items to: {run_output_dir}")

    all_csv_data = []
    used_ids = set()
    
    # Global counters
    total_processed_count = 0
    total_skipped_count = 0
    
    passage_cache = {}

    # 4. Iterate through selected standards
    for standard_folder in selected_standards:
        print(f"\n---> Standard: {standard_folder}")
        
        file_paths = get_results_file(standard_folder)
        if not file_paths: continue

        for file_path in file_paths:
            file_name_only = os.path.basename(file_path)
            print(f"     ... Breaking up file: {file_name_only}")
            
            # File-specific counters
            file_new_count = 0
            file_skipped_count = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            blocks = re.split(r'=+\s*NEW ITEM\s*=+', content, flags=re.IGNORECASE)

            for block in blocks:
                if not re.search(r'(Question:|Item:|\d\.)', block): 
                    continue

                # Generate ID
                while True:
                    item_id = str(random.randint(10000, 99999))
                    if item_id not in used_ids:
                        used_ids.add(item_id)
                        break

                # Extract Metadata
                meta_match = re.search(r'(Tier\s+\w+)\s*\((.*?)\).*?temp=([\d.]+)', block)
                tier = meta_match.group(1) if meta_match else "N/A"
                llm = meta_match.group(2) if meta_match else "N/A"
                temp = meta_match.group(3) if meta_match else "N/A"
                
                time_match = re.search(r'\(([\d.]+)\s*secs\)', block)
                elapsed_time = time_match.group(1) if time_match else "N/A"

                token_match = re.search(r'\((\d+)\s*\+\s*(\d+)\s*=\s*(\d+)\s+total\s+tokens\)', block)
                if token_match:
                    input_tokens, output_tokens, total_tokens = token_match.groups()
                else:
                    in_tok = re.search(r'Input Tokens:\s*(\d+)', block)
                    out_tok = re.search(r'Output Tokens:\s*(\d+)', block)
                    tot_tok = re.search(r'Total Tokens:\s*(\d+)', block)
                    input_tokens = in_tok.group(1) if in_tok else "N/A"
                    output_tokens = out_tok.group(1) if out_tok else "N/A"
                    total_tokens = tot_tok.group(1) if tot_tok else "N/A"

                # Extract Passage Name
                passage_match = re.search(r'Passage:.*?\s+(.*)\.txt', block)
                passage_filename = passage_match.group(1).strip() + ".txt" if passage_match else None

                # Clean Text
                cleaned_body = block.strip()
                cleaned_body = re.sub(r'\\\\', '', cleaned_body)
                
                # Cleaning sequence
                cleaned_body = re.sub(r'^Passage:.*(\n|$)', '', cleaned_body, flags=re.MULTILINE)
                cleaned_body = re.sub(r'^Tier\s+\w+.*(\n|$)', '', cleaned_body, flags=re.MULTILINE)
                cleaned_body = re.sub(r'^=+\s*NEW RUN.*(\n|$)', '', cleaned_body, flags=re.MULTILINE)
                cleaned_body = cleaned_body.strip()

                # --- DUPLICATE CHECK ---
                item_checksum = hashlib.sha256(cleaned_body.encode('utf-8')).hexdigest()
                
                if item_checksum in seen_checksums:
                    file_skipped_count += 1
                    total_skipped_count += 1
                    continue # SKIP saving this item
                
                # Add to seen list
                seen_checksums.add(item_checksum)
                # -----------------------

                # Fetch Passage Content
                full_passage_content = ""
                if passage_filename:
                    if passage_filename not in passage_cache:
                        passage_cache[passage_filename] = get_passage_text(passage_filename)
                    full_passage_content = passage_cache[passage_filename]

                # Save Item File (Content + Passage)
                safe_passage_name = passage_filename if passage_filename else "Unknown_Passage"
                item_file_name = f"{standard_folder.strip()} {item_id} {safe_passage_name}"
                
                file_content = (
                    f"Standard: {standard_folder}\n"
                    f"ID: {item_id}\n"
                    f"Passage: {safe_passage_name}\n\n"
                    f"{cleaned_body}"
                    f"{full_passage_content}"
                )
                
                with open(os.path.join(run_output_dir, item_file_name), 'w', encoding='utf-8') as out_f:
                    out_f.write(file_content)

                # Log to list (Adding Checksum)
                all_csv_data.append({
                    "Run Timestamp": run_folder_name, 
                    "Random ID": item_id,
                    "Standard": standard_folder,
                    "Passage": safe_passage_name,
                    "Tier": tier,
                    "LLM": llm,
                    "Temperature": temp,
                    "Input Tokens": input_tokens,
                    "Output Tokens": output_tokens,
                    "Total Tokens": total_tokens,
                    "Elapsed Time": elapsed_time,
                    "Checksum": item_checksum 
                })
                file_new_count += 1
                total_processed_count += 1
            
            # Print file-level stats
            print(f"         * {file_new_count} new items added.")
            print(f"         * {file_skipped_count} duplicate items rejected.")

    # 5. Handle CSV Logging (Append to MASTER log)
    if all_csv_data:
        csv_fields = [
            "Run Timestamp", "Random ID", "Standard", "Passage", 
            "Tier", "LLM", "Temperature", "Input Tokens", 
            "Output Tokens", "Total Tokens", "Elapsed Time", "Checksum"
        ]
        
        file_exists = os.path.isfile(csv_filename)
        
        with open(csv_filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=csv_fields)
            if not file_exists:
                writer.writeheader()
            writer.writerows(all_csv_data)
        
        print(f"\nLog updated: {csv_filename}")

    # Final Summary
    print("\n" + "="*30)
    print("       FINAL SUMMARY")
    print("="*30)
    print(f"Total new items added:      {total_processed_count}")
    print(f"Total duplicates rejected:  {total_skipped_count}")
    print("="*30)

if __name__ == "__main__":
    process_items()