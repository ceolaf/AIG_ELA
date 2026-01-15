import re
import random
import os
import csv
from datetime import datetime

def get_valid_standard_folder():
    # Pattern: RL 8.4, RI 9-10.1, etc.
    pattern = re.compile(r"^R[LI][ .]?(?:\d|9-10|11-12)\.\d+$", re.IGNORECASE)
    folders = [f for f in os.listdir('.') if os.path.isdir(f) and pattern.match(f)]
    
    if not folders:
        print("No folders found matching the Standard pattern (e.g., 'RL 8.4').")
        return None
    
    print("\nAvailable Standard Folders:")
    for i, folder in enumerate(folders, 1):
        print(f"{i}. {folder}")
    
    try:
        choice = input("\nSelect a folder number: ")
        return folders[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None

def get_results_file(base_folder):
    # UPDATED: Finds folders with 'result' anywhere in the name
    results_dirs = [d for d in os.listdir(base_folder) 
                    if os.path.isdir(os.path.join(base_folder, d)) and 'result' in d.lower()]
    
    if not results_dirs:
        print(f"No folders containing 'Result' found inside {base_folder}.")
        return []
    
    if len(results_dirs) == 1:
        res_dir = results_dirs[0]
        print(f"Using results folder: {res_dir}")
    else:
        print("\nMultiple Results folders found:")
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
        print("No .txt files found in the results folder.")
        return []
        
    print("\nAvailable text files:")
    print("0. Process ALL files")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f}")
    
    try:
        choice_str = input("\nSelect a file number (or 0 for all): ")
        choice = int(choice_str)
        if choice == 0:
            return [os.path.join(target_path, f) for f in files]
        else:
            return [os.path.join(target_path, files[choice - 1])]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return []

def process_items():
    standard_folder = get_valid_standard_folder()
    if not standard_folder: return

    file_paths = get_results_file(standard_folder)
    if not file_paths: return

    # ONE shared output folder for all items
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    output_dir = f"Individual Items {timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    all_csv_data = []
    used_ids = set()
    total_processed_count = 0

    for file_path in file_paths:
        file_name_only = os.path.basename(file_path)
        print(f"\n>>> Processing: {file_name_only}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        blocks = re.split(r'=+\s*NEW ITEM\s*=+', content, flags=re.IGNORECASE)

        for block in blocks:
            # Skip empty blocks or those without questions
            if not re.search(r'(Question:|Item:|\d\.)', block): 
                continue

            # 1. Generate ID
            while True:
                item_id = str(random.randint(10000, 99999))
                if item_id not in used_ids:
                    used_ids.add(item_id)
                    break

            # 2. Extract Metadata (FIXED REGEX)
            meta_match = re.search(r'(Tier\s+\w+)\s*\((.*?)\).*?temp=([\d.]+)', block)
            tier = meta_match.group(1) if meta_match else "N/A"
            llm = meta_match.group(2) if meta_match else "N/A"
            temp = meta_match.group(3) if meta_match else "N/A"
            
            # Extract Elapsed Time (e.g., 10.58 secs)
            time_match = re.search(r'\(([\d.]+)\s*secs\)', block)
            elapsed_time = time_match.group(1) if time_match else "N/A"

            # Extract Tokens (e.g., 1897 + 464 = 2361 total tokens)
            token_match = re.search(r'\((\d+)\s*\+\s*(\d+)\s*=\s*(\d+)\s+total\s+tokens\)', block)
            if token_match:
                input_tokens = token_match.group(1)
                output_tokens = token_match.group(2)
                total_tokens = token_match.group(3)
            else:
                # Fallback to old style if exists
                in_tok = re.search(r'Input Tokens:\s*(\d+)', block)
                out_tok = re.search(r'Output Tokens:\s*(\d+)', block)
                tot_tok = re.search(r'Total Tokens:\s*(\d+)', block)
                input_tokens = in_tok.group(1) if in_tok else "N/A"
                output_tokens = out_tok.group(1) if out_tok else "N/A"
                total_tokens = tot_tok.group(1) if tot_tok else "N/A"

            # 3. Extract Passage Name
            passage_match = re.search(r'Passage:.*?\s+(.*)\.txt', block)
            passage_name = passage_match.group(1).strip() if passage_match else "Unknown_Passage"

            # 4. Clean Text (Temporary: keeping raw block)
            # cleaned_body = re.sub(r'Tier\s+[\w\s]+\(.*?temp=.*?\)\n?', '', block)
            # cleaned_body = re.sub(r'Passage:.*?\n?', '', cleaned_body)
            # cleaned_body = re.sub(r'(Input|Output|Total) Tokens:.*?\n?', '', cleaned_body)
            cleaned_body = block.strip()
            cleaned_body = re.sub(r'\\\\', '', cleaned_body)

            # 5. Save Item File
            item_file_name = f"{standard_folder} {item_id} {passage_name}.txt"
            file_content = f"Standard: {standard_folder}\nID: {item_id}\nPassage: {passage_name}\n\n{cleaned_body}"
            
            with open(os.path.join(output_dir, item_file_name), 'w', encoding='utf-8') as out_f:
                out_f.write(file_content)

            # 6. Log to list
            all_csv_data.append({
                "Random ID": item_id,
                "Standard": standard_folder,
                "Passage": passage_name,
                "Tier": tier,
                "LLM": llm,
                "Temperature": temp,
                "Input Tokens": input_tokens,
                "Output Tokens": output_tokens,
                "Total Tokens": total_tokens,
                "Elapsed Time": elapsed_time
            })
            total_processed_count += 1

    # Save final CSV
    if all_csv_data:
        csv_filename = os.path.join(output_dir, "item_metadata_log.csv")
        csv_fields = ["Random ID", "Standard", "Passage", "Tier", "LLM", "Temperature", "Input Tokens", "Output Tokens", "Total Tokens", "Elapsed Time"]
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=csv_fields)
            writer.writeheader()
            writer.writerows(all_csv_data)

    print(f"\nFinished! {total_processed_count} total items saved to: {output_dir}")

if __name__ == "__main__":
    process_items()