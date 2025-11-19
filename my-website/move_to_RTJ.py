import os
import shutil
import re

# Function to delete specific folders and recreate them to ensure a clean slate
def delete_folders(folder_path, folders_to_delete):
    for folder in folders_to_delete:
        full_path = os.path.join(folder_path, folder)
        if os.path.exists(full_path):
            print(f"Deleting and recreating: {full_path}")
            # 1. Delete the folder and its contents
            shutil.rmtree(full_path)
            # 2. Recreate the empty folder to ensure path exists for copy later
            os.makedirs(full_path)
        # If it doesn't exist, we'll create it later in copy_files_and_folders if it's in the source.

# Function to copy all files and folders, filtering out duplicates
def copy_files_and_folders(source_folder, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        
    for item in os.listdir(source_folder):
        # --- FIX: Filter out duplicate files (e.g., file.1.md, file 1.md) ---
        if re.search(r'\.\d+\.md$', item) or re.search(r' \d+\.md$', item):
            print(f"Skipping sync conflict file: {item}")
            continue

        src_path = os.path.join(source_folder, item)
        dest_path = os.path.join(destination_folder, item)
        
        if os.path.isdir(src_path):
            # This handles both creating a new directory and merging/overwriting into an existing one
            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
        else:
            # Overwrite top-level files like 'Getting started.md'
            shutil.copy2(src_path, dest_path)

# Function to process markdown files (link conversion and admonition fix)
def process_files(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".md"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Remove "docs/sidebar1/" from the content to fix internal links
                content = content.replace("docs/sidebar1/", "")

                # Process admonition blocks (Docusaurus to Obsidian Callouts)
                admonition_types = ['tip', 'note', 'warning', 'danger', 'info']
                for atype in admonition_types:
                    # Use a robust search pattern for the Docusaurus admonition block
                    docusaurus_admonition_pattern = rf"(:::{atype}.*?:::)"
                    
                    def convert_admonition(match):
                        admonition = match.group(0)
                        lines = admonition.splitlines()
                        
                        # Extract and format the title line
                        title_line = lines[0].replace(f":::{atype}", "").strip()
                        if title_line:
                            title_line = f"> [!{atype}] {title_line}"
                        else:
                            title_line = f"> [!{atype}]"
                            
                        # Format the body lines
                        body_lines = [f"> {line}" for line in lines[1:-1]]
                        
                        # Reconstruct the Obsidian Callout format
                        return f"{title_line}\n" + "\n".join(body_lines) + "\n"

                    # Replace all occurrences using the helper function
                    content = re.sub(docusaurus_admonition_pattern, convert_admonition, content, flags=re.DOTALL)
                    
                # Write the modified content back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

# Function to compress destination folder into a zip file
def compress_folder(folder_path, output_zip):
    shutil.make_archive(output_zip, 'zip', folder_path)

# Main function
def main():
    source_folder = "/Users/imedgh/Documents/roadmap-to-janna/my-website/docs/sidebar1"
    destination_folder = "/Users/imedgh/Documents/roadmap-to-janna/my-website/assets/RTJ"
    
    # --- Folders to completely clear before copying new content ---
    # Includes the current 'Objective' folder, 'Processes', and 'Resources'.
    # 'Initiatives' is included as a cleanup measure for previous runs.
    folders_to_clear_before_copy = ["Objective", "Processes", "Resources"] 
    
    output_zip = "/Users/imedgh/Documents/roadmap-to-janna/my-website/assets/RTJ"

    print("Step 1: Cleaning specified subfolders (Objective, Processes, Resources) in the destination vault...")
    delete_folders(destination_folder, folders_to_clear_before_copy)

    print("Step 2: Copying files...")
    copy_files_and_folders(source_folder, destination_folder)

    print("Step 3: Processing markdown links and callouts...")
    process_files(destination_folder)

    print("Step 4: Zipping folder...")
    compress_folder(destination_folder, output_zip)
    
    print("Done!")

if __name__ == "__main__":
    main()