import os
import shutil
import yaml
import re
import fnmatch
import hashlib
import tempfile
from collections import defaultdict

# -------------------------
# Basic helpers
# -------------------------
def load_frontmatter(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    if isinstance(frontmatter, dict):
                        body = parts[2].strip()
                        return frontmatter, body
                except yaml.YAMLError as e:
                    print(f"YAML parse error in {file_path}: {e}")
                    return None, None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return None, None

# -------------------------
# Atomic write + logging
# -------------------------
def atomic_write(file_path, content_bytes):
    dest_dir = os.path.dirname(file_path)
    os.makedirs(dest_dir, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp_write_", dir=dest_dir)
    try:
        with os.fdopen(fd, 'wb') as tmpf:
            tmpf.write(content_bytes)
        os.replace(tmp_path, file_path)
    except Exception as e:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        raise e

def write_if_changed_atomic(file_path, frontmatter, body):
    text = "---\n" + yaml.dump(frontmatter, default_flow_style=False, sort_keys=False) + "---\n\n" + body
    content_bytes = text.encode('utf-8')

    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as f:
                existing = f.read()
            if existing == content_bytes:
                print(f"[skip] identical: {file_path}")
                return
        except Exception as e:
            print(f"[warn] couldn't open existing file {file_path} for compare: {e}")

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    atomic_write(file_path, content_bytes)
    print(f"[write] {file_path}")

# -------------------------
# Transforms & Link Logic (The Fix is Here)
# -------------------------
def process_frontmatter(frontmatter, filename):
    label = filename[:-3] if filename.endswith(".md") else filename
    # Clean label for sidebar (remove .2, etc)
    clean_label = re.sub(r'(?:\s*\(\d+\)|\.\d+|\s+\d+)$', '', label)
    frontmatter["sidebar_label"] = clean_label

    for f in ["start", "due", "recurrence", "context", "dependency"]:
        if f in frontmatter:
            frontmatter[f] = ""
    for f in ["duration", "detail"]:
        if f in frontmatter:
            frontmatter[f] = None
    for f in ["delay", "blocking", "outcome", "driver", "tracking", "religious", "behavior"]:
        if f in frontmatter:
            del frontmatter[f]

    if "status" in frontmatter:
        if frontmatter.get("type") == "process":
            frontmatter["status"] = ""
        if frontmatter.get("type") == "domain":
            frontmatter["status"] = "designed"

    if "domain" in frontmatter:
        domains = frontmatter["domain"]
        if isinstance(domains, str):
            domains = [domains]
        cleaned = []
        for d in domains:
            m = re.search(r"\|([^]]+)", d)
            if m:
                cleaned.append(f"[[{m.group(1)}]]")
            else:
                cleaned.append(d)
        frontmatter["domain"] = cleaned

    return frontmatter

def transform_links(body, domain_mapping):
    # 1. Helper to get the LOOKUP name (spaces, no suffixes)
    def clean_link_target(fname):
        # Decode %20 to space so we can find it in our dictionary
        fname = os.path.basename(fname).replace("%20", " ")
        if fname.endswith(".md"):
            fname = fname[:-3]
        # Normalize (remove .2, (1), etc) to match how we stored keys
        fname = normalize_basename_for_grouping(fname) 
        return fname

    # 2. Helper to generate the URL path (ensuring %20 is used)
    def get_new_path(clean_name):
        # IMPORTANT: Re-encode spaces to %20 for the final URL string
        url_name = clean_name.replace(" ", "%20")
        
        if clean_name in domain_mapping:
            obj = domain_mapping[clean_name].get("objective", "")
            if obj == "remove bad traits":
                # Note: bad%20traits is hardcoded, and we use url_name for the file
                return f"docs/sidebar1/Objective/bad%20traits/{url_name}.md"
            elif obj == "have good traits":
                return f"docs/sidebar1/Objective/good%20traits/{url_name}.md"
            elif obj == "worship well":
                return f"docs/sidebar1/Objective/worship/{url_name}.md"
            else:
                return f"docs/sidebar1/Objective/{url_name}.md"
        else:
            return f"docs/sidebar1/Processes/{url_name}.md"

    def bracket(match):
        raw_name = match.group(1)
        clean_name = clean_link_target(raw_name)
        new_path = get_new_path(clean_name)
        return f"[{clean_name}]({new_path})"

    def markdown(match):
        text, link = match.groups()
        clean_name = clean_link_target(link)
        new_path = get_new_path(clean_name)
        return f"[{text}]({new_path})"

    # Regex replacers
    body = re.sub(r"\[([^\]]+)\]\((?!http)([^)]+)\)", markdown, body)
    body = re.sub(r"\[\[([^\]]+)\]\]", bracket, body)
    return body

def convert_obsidian_to_docusaurus(text):
    lines = text.splitlines()
    result = []
    in_callout = False
    callout_type = None
    callout_body = []

    for line in lines:
        if line.startswith("> [!"):
            if in_callout:
                result.append(f":::{callout_type} {callout_body[0]}")
                result.append("\n".join(callout_body[1:]))
                result.append(":::")
            in_callout = True
            callout_type = line[4:line.find("]")]
            callout_body = [line[line.find("]") + 1:].strip()]
        elif in_callout:
            if line.startswith(">"):
                callout_body.append(line[2:].strip())
            else:
                result.append(f":::{callout_type} {callout_body[0]}")
                result.append("\n".join(callout_body[1:]))
                result.append(":::")
                in_callout = False
                result.append(line)
        else:
            result.append(line)

    if in_callout:
        result.append(f":::{callout_type} {callout_body[0]}")
        result.append("\n".join(callout_body[1:]))
        result.append(":::")

    return "\n".join(result)

def remove_private_section(content):
    idx = content.find("# private")
    if idx != -1:
        return content[:idx].strip()
    return content

# -------------------------
# Normalization & Main Logic
# -------------------------
_suffix_re = re.compile(r'(?:\s*\(\d+\)|\.\d+|\s+\d+| - Copy(?: \(\d+\))?)$')

def normalize_basename_for_grouping(filename):
    if filename.lower().endswith(".md"):
        stem = filename[:-3]
    else:
        stem = filename
    
    prev = None
    while prev != stem:
        prev = stem
        stem = _suffix_re.sub("", stem)
    
    return stem.strip()

def copy_and_process_files(source_folders, destination_folders):
    vault = source_folders["vault"]

    # 1. Build Mapping
    domain_mapping = {}
    for root, dirs, files in os.walk(vault):
        for f in files:
            if not f.endswith(".md"):
                continue
            fp = os.path.join(root, f)
            fm, _ = load_frontmatter(fp)
            if fm and fm.get("type") == "domain":
                norm_name = normalize_basename_for_grouping(f)
                domain_mapping[norm_name] = fm

    # 2. Collect Candidates
    domain_candidates = defaultdict(list)
    process_candidates = defaultdict(list)

    def has_religious(front):
        if "domain" not in front: return False
        ds = front["domain"]
        if isinstance(ds, str): ds = [ds]
        for d in ds:
            m = re.search(r"\|([^]]+)", d)
            if not m: m = re.search(r"\[\[([^]]+)\]\]", d)
            name = m.group(1) if m else d.replace("[[", "").replace("]]", "")
            norm_ref = normalize_basename_for_grouping(name)
            if norm_ref in domain_mapping and domain_mapping[norm_ref].get("religious"):
                return True
        return False

    for root, dirs, files in os.walk(vault):
        for f in files:
            if not f.endswith(".md"): continue
            fp = os.path.join(root, f)
            fm, body = load_frontmatter(fp)
            if not fm: continue
            
            mtime = os.path.getmtime(fp)
            norm_name = normalize_basename_for_grouping(f)

            if fm.get("type") == "domain":
                obj = fm.get("objective", "")
                if obj in ("remove bad traits", "have good traits", "worship well"):
                    domain_candidates[norm_name].append((fp, mtime, f, obj))
            elif fm.get("type") == "process":
                if has_religious(fm):
                    if not any(existing_fp == fp for (existing_fp, _, _, _) in process_candidates[norm_name]):
                        process_candidates[norm_name].append((fp, mtime, f, None))

    # 3. Select Best Candidates
    final_domains = {}
    for norm, lst in domain_candidates.items():
        final_domains[norm] = max(lst, key=lambda x: x[1])

    final_processes = {}
    for norm, lst in process_candidates.items():
        final_processes[norm] = max(lst, key=lambda x: x[1])

    # 4. Clean Dests
    for folder in destination_folders.values():
        if os.path.exists(folder): shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

    written_records = defaultdict(dict)

    # 5. Write
    for norm_name, (src_path, mtime, orig_name, objective) in final_domains.items():
        fm, body = load_frontmatter(src_path)
        if not fm: continue

        if objective == "remove bad traits": dest_folder = destination_folders["bad_traits"]
        elif objective == "have good traits": dest_folder = destination_folders["good_traits"]
        elif objective == "worship well": dest_folder = destination_folders["worship_actions"]
        else: continue

        dest_filename = norm_name + ".md"
        dest_path = os.path.join(dest_folder, dest_filename)

        body = transform_links(body, domain_mapping)
        body = convert_obsidian_to_docusaurus(body)
        body = remove_private_section(body)
        fm = process_frontmatter(fm, dest_filename)

        write_if_changed_atomic(dest_path, fm, body)
        written_records[dest_folder][dest_filename] = (src_path, mtime)

    for norm_name, (src_path, mtime, orig_name, _) in final_processes.items():
        fm, body = load_frontmatter(src_path)
        if not fm: continue

        dest_folder = destination_folders["processes"]
        dest_filename = norm_name + ".md"
        dest_path = os.path.join(dest_folder, dest_filename)

        body = transform_links(body, domain_mapping)
        body = convert_obsidian_to_docusaurus(body)
        body = remove_private_section(body)
        fm = process_frontmatter(fm, dest_filename)

        write_if_changed_atomic(dest_path, fm, body)
        written_records[dest_folder][dest_filename] = (src_path, mtime)

    print("\n[summary] Processing complete.")
    print(f"Processed {len(written_records)} folders.")

# -------------------------
# Config
# -------------------------
def main():
    source = {
        "vault": "/Users/imedgh/Desktop/vault/"
    }
    dest = {
        "processes": "/Users/imedgh/Documents/roadmap-to-janna/my-website/docs/sidebar1/Processes",
        "bad_traits": "/Users/imedgh/Documents/roadmap-to-janna/my-website/docs/sidebar1/Objective/bad traits",
        "good_traits": "/Users/imedgh/Documents/roadmap-to-janna/my-website/docs/sidebar1/Objective/good traits",
        "worship_actions": "/Users/imedgh/Documents/roadmap-to-janna/my-website/docs/sidebar1/Objective/worship"
    }

    copy_and_process_files(source, dest)

if __name__ == "__main__":
    main()