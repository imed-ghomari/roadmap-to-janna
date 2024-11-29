import os
import shutil
import yaml
import re
from collections import OrderedDict

# Load YAML frontmatter from a file
def load_frontmatter(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if content.startswith("---"):
        parts = content.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])
        body = parts[2].strip()
        return frontmatter, body
    return None, None

# Write frontmatter and body back to a file
def write_frontmatter(file_path, frontmatter, body):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("---\n")
        yaml.dump(frontmatter, f, default_flow_style=False, sort_keys=False)
        f.write("---\n\n")
        f.write(body)



# Process frontmatter properties
def process_frontmatter(frontmatter):
    if "waiting" in frontmatter:
        frontmatter["waiting"] = False
    if "start" in frontmatter:
        frontmatter["start"] = ""
    if "due" in frontmatter:
        frontmatter["due"] = ""
    if "working" in frontmatter:
        frontmatter["working"] = False
    if "duration" in frontmatter:
        frontmatter["duration"] = None
    if "recurrence" in frontmatter:
        frontmatter["recurrence"] = ""
    if "review" in frontmatter:
        frontmatter["review"] = ""
    if "file" in frontmatter:
        frontmatter["file"] = ""
    if "context" in frontmatter:
        frontmatter["context"] = ""
    if "dependency" in frontmatter:
        frontmatter["dependency"] = ""
    if "step" in frontmatter:
        frontmatter["step"] = ""
    if "religious" in frontmatter:  # Remove the 'religious' property
        del frontmatter["religious"]

    # Modify the 'initiative' property
    if "initiative" in frontmatter:
        initiatives = frontmatter["initiative"]
        updated_initiatives = []
        for initiative in initiatives:
            # Use regex to extract the part after the '|' in each link
            match = re.search(r"\|([^]]+)", initiative)
            if match:
                updated_initiatives.append(f"[[{match.group(1)}]]")
        frontmatter["initiative"] = updated_initiatives

    return frontmatter


# Transform links in the body
def transform_links(body, initiative_mapping):
    def replace_link_brackets(match):
        filename = match.group(1)
        filename = os.path.basename(filename).replace("%20", " ")
        
        if filename.endswith(".md"):
            filename = filename[:-3]

        if filename in initiative_mapping:
            initiative_data = initiative_mapping[filename]
            kr = initiative_data.get("KR", "")
            if kr == "bad traits":
                new_link = f"docs/sidebar1/Initiatives/bad%20traits/{filename.replace(' ', '%20')}.md"
            elif kr == "good traits":
                new_link = f"docs/sidebar1/Initiatives/good%20traits/{filename.replace(' ', '%20')}.md"
            elif kr == "worship actions":
                new_link = f"docs/sidebar1/Initiatives/worship/{filename.replace(' ', '%20')}.md"
            else:
                new_link = f"docs/sidebar1/Initiatives/{filename.replace(' ', '%20')}.md"
        else:
            new_link = f"docs/sidebar1/Processes/{filename.replace(' ', '%20')}.md"
        return f"[{filename}]({new_link})"

    def replace_link_markdown(match):
        text, link = match.groups()
        filename = os.path.basename(link).replace("%20", " ")
        
        if filename.endswith(".md"):
            filename = filename[:-3]

        if filename in initiative_mapping:
            initiative_data = initiative_mapping[filename]
            kr = initiative_data.get("KR", "")
            if kr == "bad traits":
                new_link = f"docs/sidebar1/Initiatives/bad%20traits/{filename.replace(' ', '%20')}.md"
            elif kr == "good traits":
                new_link = f"docs/sidebar1/Initiatives/good%20traits/{filename.replace(' ', '%20')}.md"
            elif kr == "worship actions":
                new_link = f"docs/sidebar1/Initiatives/worship/{filename.replace(' ', '%20')}.md"
            else:
                new_link = f"docs/sidebar1/Initiatives/{filename.replace(' ', '%20')}.md"
        else:
            new_link = f"docs/sidebar1/Processes/{filename.replace(' ', '%20')}.md"
        return f"[{text}]({new_link})"

    # Process Markdown-style links [text](link) but exclude web links
    body = re.sub(r'\[([^\]]+)\]\((?!http[s]?:)([^)]+)\)', replace_link_markdown, body)

    # Process Obsidian-style links [[filename]] but exclude web links
    body = re.sub(r'\[\[([^\]]+)\]\](?!http[s]?:)', replace_link_brackets, body)

    return body

# Convert Obsidian-style callouts to Docusaurus-style
def convert_obsidian_to_docusaurus(content):
    lines = content.splitlines()
    result = []
    in_callout, callout_type, callout_body = False, None, []

    for line in lines:
        if line.startswith("> [!"):
            if in_callout:
                # Join all lines and add the callout properly with formatted body
                result.append(f":::{callout_type} {callout_body[0]}")
                result.append("\n".join(callout_body[1:]).strip())  # Preserve line breaks
                result.append(":::")
            in_callout = True
            callout_type = line[4:line.find(']')]
            callout_body = [line[line.find(']')+1:].strip()]
        elif in_callout:
            if line.startswith(">"):  # Continuation of callout
                callout_body.append(line[2:].strip())  # Add subsequent lines to body
            else:
                # End the current callout and append to the result
                result.append(f":::{callout_type} {callout_body[0]}")
                result.append("\n".join(callout_body[1:]).strip())  # Add multi-line content correctly
                result.append(":::")
                in_callout = False
                result.append(line)  # Add non-callout line to result
        else:
            result.append(line)

    if in_callout:  # Handle the case when the last callout doesn't have a non-callout line
        result.append(f":::{callout_type} {callout_body[0]}")
        result.append("\n".join(callout_body[1:]).strip())
        result.append(":::")

    return "\n".join(result)

# Function to remove content after "# private"
def remove_private_section(content):
    private_section_index = content.find("# private")
    if private_section_index != -1:
        content = content[:private_section_index].strip()
    return content

# Process markdown files in a folder
def process_files(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".md"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                content = convert_obsidian_to_docusaurus(content)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

# Copy and process files
def copy_and_process_files(source_folders, destination_folders):
    initiative_mapping = {}

    for root, _, files in os.walk(source_folders['initiatives']):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".md"):
                frontmatter, _ = load_frontmatter(file_path)
                if not frontmatter:
                    continue
                if frontmatter.get("type") == "initiative" and frontmatter.get("religious") == True:
                    initiative_mapping[file[:-3]] = frontmatter

    for root, _, files in os.walk(source_folders['initiatives']):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".md"):
                frontmatter, body = load_frontmatter(file_path)
                if not frontmatter:
                    continue
                kr = frontmatter.get("KR", "")
                if kr == "bad traits":
                    destination = os.path.join(destination_folders['bad_traits'], file)
                elif kr == "good traits":
                    destination = os.path.join(destination_folders['good_traits'], file)
                elif kr == "worship actions":
                    destination = os.path.join(destination_folders['worship_actions'], file)
                else:
                    continue
                body = transform_links(body, initiative_mapping)
                body = convert_obsidian_to_docusaurus(body)
                body = remove_private_section(body)
                frontmatter = process_frontmatter(frontmatter)
                write_frontmatter(destination, frontmatter, body)

    # Process files in the 'processes' folder
    for root, _, files in os.walk(source_folders['processes']):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".md"):
                frontmatter, body = load_frontmatter(file_path)
                if not frontmatter:
                    print(f"Skipping file without valid frontmatter: {file}")
                    continue

                destination = os.path.join(destination_folders['processes'], file)
                print(f"Processing process file: {file}")

                # Transformations
                body = transform_links(body, initiative_mapping)
                body = remove_private_section(body)
                body = convert_obsidian_to_docusaurus(body)
                frontmatter = process_frontmatter(frontmatter)
                write_frontmatter(destination, frontmatter, body)


def main():
    # Define source and destination folders explicitly
    source_folders = {
        'initiatives': "/Users/imedgh/Desktop/vault/Initiatives",
        'processes': "/Users/imedgh/Desktop/vault/Processes"
    }
    destination_folders = {
        'processes': "/Users/imedgh/Documents/roadmap-to-janna/my-website/docs/sidebar1/Processes",
        'bad_traits': "/Users/imedgh/Documents/roadmap-to-janna/my-website/docs/sidebar1/Initiatives/bad traits",
        'good_traits': "/Users/imedgh/Documents/roadmap-to-janna/my-website/docs/sidebar1/Initiatives/good traits",
        'worship_actions': "/Users/imedgh/Documents/roadmap-to-janna/my-website/docs/sidebar1/Initiatives/worship"
    }

    # Ensure destination folders exist or create them
    for folder in destination_folders.values():
        os.makedirs(folder, exist_ok=True)  # Allow existing directories

    # Process files
    copy_and_process_files(source_folders, destination_folders)

if __name__ == "__main__":
    main()