import os
import requests
from markdownify import markdownify as md

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

def convert_to_hugo_md(discussion):
    title = discussion['title']
    body = md(discussion['body'])
    # Get discussion labels/tags if available
    labels = discussion.get('labels', [])
    if isinstance(labels, dict):
        labels = labels.get('nodes', [])
    tags = [label['name'] for label in labels] if labels else []
    category = discussion.get('category', {}).get('name', '')
    md_content = f"""---
title: "{title}"
date: {discussion.get('created_at', '')}
tags: {tags}
categories: ["{category}"]
---
{body}
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
