import os
import shutil

# Function to delete specific folders in the destination
def delete_folders(folder_path, folders_to_delete):
    for folder in folders_to_delete:
        full_path = os.path.join(folder_path, folder)
        if os.path.exists(full_path):
            shutil.rmtree(full_path)  # Delete only the specified folder

# Function to copy all files and folders, replacing any existing files
def copy_files_and_folders(source_folder, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)  # Create the destination folder if it doesn't exist
    for item in os.listdir(source_folder):
        src_path = os.path.join(source_folder, item)
        dest_path = os.path.join(destination_folder, item)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)  # Replace any existing directory
        else:
            shutil.copy2(src_path, dest_path)  # Replace any existing file

# Function to process markdown files
def process_files(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".md"):  # Process markdown files only
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Remove "docs/sidebar1/" from the content
                content = content.replace("docs/sidebar1/", "")

                # Process admonition blocks
                admonition_types = ['tip', 'note', 'warning', 'danger', 'info']
                for atype in admonition_types:
                    while f":::{atype}" in content:
                        start_idx = content.find(f":::{atype}")
                        end_idx = content.find(":::", start_idx + 1) + 3
                        admonition = content[start_idx:end_idx]

                        # Extract the title and body
                        lines = admonition.splitlines()
                        title_line = lines[0].replace(f":::{atype}", f"> [!{atype}]")
                        body_lines = lines[1:-1]  # Exclude the first and last lines (::: markers)

                        # Add `>` to each line of the body
                        formatted_body = "\n".join(f"> {line}" for line in body_lines)

                        # Combine title and body
                        formatted_admonition = f"{title_line}\n> \n{formatted_body}\n"

                        # Replace the original admonition with the formatted one
                        content = content.replace(admonition, formatted_admonition)

                # Write the modified content back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

# Function to compress destination folder into a zip file
def compress_folder(folder_path, output_zip):
    shutil.make_archive(output_zip, 'zip', folder_path)

# Main function
def main():
    source_folder = "/Users/imedgh/Documents/roadmap-to-janna/my-website/docs/sidebar1"  # Replace with the source folder path
    destination_folder = "/Users/imedgh/Documents/roadmap-to-janna/my-website/assets/RTJ"  # Replace with the destination folder path
    folders_to_delete = ["Initiatives", "Processes", "Resources"]  # Replace with folders to delete
    output_zip = "/Users/imedgh/Documents/roadmap-to-janna/my-website/assets/RTJ"  # Replace with the desired output zip path (without extension)

    # Step 1: Delete specified folders in the destination folder
    delete_folders(destination_folder, folders_to_delete)

    # Step 2: Copy all files and folders from the source to the destination
    copy_files_and_folders(source_folder, destination_folder)

    # Step 3: Process markdown files in the destination folder
    process_files(destination_folder)

    # Step 4: Compress the destination folder into a zip file
    compress_folder(destination_folder, output_zip)

if __name__ == "__main__":
    main()
