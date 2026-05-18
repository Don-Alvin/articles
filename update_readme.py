import os
import re
from datetime import datetime
from pathlib import Path

def find_articles(base_path="."):
    articles = {}
    topic_pattern = re.compile(r"^\d{2}-(.+)$")

    for topic_dir in sorted(Path(base_path).iterdir()):
        if not topic_dir.is_dir():
            continue
        match = topic_pattern.match(topic_dir.name)
        if not match:
            continue

        topic_key = topic_dir.name
        articles[topic_key] = []

        for article_dir in topic_dir.iterdir():
            if not article_dir.is_dir():
                continue
            article_file = article_dir / "index.md"
            if not article_file.exists():
                article_file = article_dir / "README.md"
            if not article_file.exists():
                continue

            # Extract date from the article file
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", article_dir.name)

            if not date_match and article_file.exists():
                content = article_file.read_text()
                date_match = re.search(r"date:\s*(\d{4}-\d{2}-\d{2})", content)
            
            date = date_match.group(1) if date_match else "Unknown Date"
            articles[topic_key].append({
                "name": article_dir.name.replace("-", " ").title(),
                "path": str(article_dir.relative_to(base_path)),
                "date": date
            })
    
    for topic in articles:
        articles[topic].sort(key=lambda x: x["date"], reverse=True)
    return articles

def update_readme(articles, readme_path="README.md"):
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Total articles count
    total = sum(len(articles[topic]) for topic in articles)
    content = content.replace("{{TOTAL_ARTICLES}}", str(total))
    content = content.replace("{{DATE}}", datetime.now().strftime("%Y-%m-%d"))

    for topic in articles:
        count = len(articles[topic])
        content = content.replace(f"{{{{COUNT_{topic}}}}}", str(count))

        latest = articles[topic][0]["date"] if articles[topic] else "N/A"
        content = content.replace(f"{{{{LATEST_{topic}}}}}", latest)
    
    with open(readme_path, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    articles = find_articles()
    update_readme(articles)