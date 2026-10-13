import json
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
BLOG_POSTS_FILE = Path(__file__).with_name("blog_posts.json")


def load_blog_posts():
    with BLOG_POSTS_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def save_blog_posts(blog_posts):
    with BLOG_POSTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(blog_posts, file, indent=2, ensure_ascii=False)
        file.write("\n")


def fetch_post_by_id(post_id):
    blog_posts = load_blog_posts()
    return next(
        (post for post in blog_posts if post["id"] == post_id),
        None,
    )


@app.route('/')
def index():
    blog_posts = load_blog_posts()
    return render_template('index.html', posts=blog_posts)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        blog_posts = load_blog_posts()
        new_post = {
            "id": max((post["id"] for post in blog_posts), default=0) + 1,
            "author": request.form.get("author"),
            "title": request.form.get("title"),
            "content": request.form.get("content"),
            "likes": 0,
        }
        blog_posts.append(new_post)
        save_blog_posts(blog_posts)

        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/delete/<int:post_id>')
def delete(post_id):
    blog_posts = load_blog_posts()
    blog_posts = [post for post in blog_posts if post["id"] != post_id]
    save_blog_posts(blog_posts)

    return redirect(url_for('index'))


@app.route('/update/<int:post_id>', methods=['GET', 'POST'])
def update(post_id):
    post = fetch_post_by_id(post_id)
    if post is None:
        return "Post not found", 404

    if request.method == 'POST':
        post["author"] = request.form.get("author")
        post["title"] = request.form.get("title")
        post["content"] = request.form.get("content")

        blog_posts = load_blog_posts()
        for index, current_post in enumerate(blog_posts):
            if current_post["id"] == post_id:
                blog_posts[index] = post
                break

        save_blog_posts(blog_posts)
        return redirect(url_for('index'))

    return render_template('update.html', post=post)


@app.route('/like/<int:post_id>')
def like(post_id):
    blog_posts = load_blog_posts()

    for post in blog_posts:
        if post["id"] == post_id:
            post["likes"] = post.get("likes", 0) + 1
            save_blog_posts(blog_posts)
            return redirect(url_for('index'))

    return "Post not found", 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
