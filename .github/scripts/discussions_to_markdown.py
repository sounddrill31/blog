import os
import requests
import yaml

github_token = os.getenv('GH_TOKEN')
repo = 'sounddrill31/blog'  # Change if needed
headers = {'Authorization': f'token {github_token}'}

def fetch_discussions():
    url = f'https://api.github.com/repos/{repo}/discussions'
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    all_discussions = resp.json()
    # Filter only Announcements category
    return [d for d in all_discussions if d.get('category', {}).get('name', '') == 'Announcements']

def extract_frontmatter(md_text):
    """Extract frontmatter as dict and body without frontmatter."""
    import re
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', md_text, re.DOTALL)
    if fm_match:
        fm_yaml = fm_match.group(1)
        body = fm_match.group(2)
        try:
            fm_dict = yaml.safe_load(fm_yaml) or {}
        except Exception:
            fm_dict = {}
        return fm_dict, body
    return {}, md_text

def convert_to_hugo_md(discussion):
    title = discussion['title']
    body_raw = discussion.get('body', '')
    old_fm, body = extract_frontmatter(body_raw.strip())

    # Get discussion labels as categories
    labels = discussion.get('labels', [])
    if isinstance(labels, dict):
        labels = labels.get('nodes', [])
    categories = [label['name'] for label in labels] if labels else []

    # Prepare new frontmatter (discussion overrides old)
    new_fm = {
        'title': title,
        'date': discussion.get('created_at', ''),
        'categories': categories if categories else [],
    }
    # Merge: old_fm keys preserved unless overridden by new_fm
    merged_fm = {**old_fm, **{k: v for k, v in new_fm.items() if v not in [None, '', []]}}

    # Dump merged frontmatter as YAML
    fm_yaml = yaml.safe_dump(merged_fm, sort_keys=False, allow_unicode=True).strip()

    md_content = f"""---
{fm_yaml}
---

{body.strip()}
"""
    return md_content

def slugify(text):
    """Convert title to URL-friendly slug"""
    import re
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def main():
    discussions = fetch_discussions()
    for d in discussions:
        slug = slugify(d['title'])
        post_dir = f"content/post/{slug}"
        os.makedirs(post_dir, exist_ok=True)
        fname = f"{post_dir}/index.md"
        with open(fname, 'w') as f:
            f.write(convert_to_hugo_md(d))

if __name__ == '__main__':
    main()
