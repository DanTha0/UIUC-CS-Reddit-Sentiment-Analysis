import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

headers = {
    "User-Agent": "UIUC-course-sentiment-scraper/1.0"
}

import json

with open("courses.json", "r") as f:
    courses = json.load(f)

course_ids = [course["id"] for course in courses]

courses = []
for course in course_ids:
    if course[0] != "5":
        courses.append("CS "+course)

# --------------------------------------------
# Scrape subreddit search results
# --------------------------------------------
def scrape_subreddit_course(subreddit, course_query, pages=3):
    base = "https://old.reddit.com"
    url = f"{base}/r/{subreddit}/search?q=%22{course_query.replace(' ', '+')}%22&restrict_sr=on&sort=new"

    posts = []

    for _ in range(pages):
        print(f"[Scraping] {url}")
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        search_results = soup.select("div.search-result a.search-title")
        if not search_results:
            print("No posts found on this page.")
            break

        for post in search_results:
            title = post.text.strip()
            post_url = post['href']
            if post_url.startswith("/"):
                post_url = base + post_url

            posts.append({
                "subreddit": subreddit,
                "course": course_query,
                "title": title,
                "url": post_url
            })

        next_btn = soup.find("span", class_="next-button")
        if not next_btn:
            break
        url = next_btn.find("a")["href"]
        time.sleep(1.5)

    return posts

# --------------------------------------------
# Scrape comments for each post
# --------------------------------------------
def scrape_comments(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    comments = []
    for comment in soup.select("div.comment div.md"):
        text = comment.get_text(strip=True)
        if text:
            comments.append(text)
            print(f"[Comment] {text[:60]}...")
    return comments

# --------------------------------------------
# Scrape courses and save
# --------------------------------------------
def scrape_courses(course_list, pages):
    all_posts = []

    for course in course_list:
        print(f"\n=== Scraping for {course} ===")
        all_posts.extend(scrape_subreddit_course("UIUC", course, pages))
        all_posts.extend(scrape_subreddit_course("UIUC_CS", course, pages))

    df = pd.DataFrame(all_posts)

    if df.empty:
        print("No posts found for any courses.")
        return df

    print("\n[Scraping Comments]")
    df["comments"] = df["url"].apply(scrape_comments)

    return df

df = scrape_courses(courses, pages=20)

# Save to pickle
df.to_pickle("uiuc_course_comments.pkl")
print(f"\nSaved {len(df)} posts and comments to uiuc_course_comments.pkl")
