import sqlite3
from flask import Flask, request, jsonify
from sqlite3 import Row
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

conn = sqlite3.connect('blog.db', check_same_thread=False)
conn.row_factory = Row  # Set the row_factory to sqlite3.Row
cursor = conn.cursor()


# Define data models
class BlogPost:
    def __init__(self, post_id, user_id, content):
        self.post_id = post_id
        self.user_id = user_id
        self.content = content
        self.comments = []

class Comment:
    def __init__(self, comment_id, post_id, user_id, content):
        self.comment_id = comment_id
        self.post_id = post_id
        self.user_id = user_id
        self.content = content


# Define routes

@app.route('/posts/', methods=['GET'])
def get_posts():
    cursor.execute('SELECT * FROM blog_posts')
    blog_post_data = cursor.fetchall()

    posts = [dict(post) for post in blog_post_data]

    for post in posts:
        cursor.execute('SELECT * FROM comments WHERE post_id = ?', (post['post_id'],))
        comments = cursor.fetchall()
        post['comments'] = len(comments)

    return jsonify(posts)

@app.route('/posts/', methods=['POST'])
def create_post():
    post = request.get_json()
    cursor.execute('''
        INSERT INTO blog_posts (user_id, title, content)
        VALUES (?, ?, ?)
    ''', (post['user_id'], post['title'], post['content']))
    conn.commit()
    return jsonify(post)


@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post_with_comments(post_id):
    cursor.execute('SELECT * FROM blog_posts WHERE post_id = ?', (post_id,))
    post = cursor.fetchone()

    cursor.execute('SELECT * FROM comments WHERE post_id = ?', (post_id,))
    comments = cursor.fetchall()

    post = dict(post)
    post['comments'] = [dict(comment) for comment in comments]
    return post

@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = request.get_json()
    cursor.execute('''
        UPDATE blog_posts
        SET user_id = ?, title = ?, content = ?
        WHERE post_id = ?
    ''', (post['user_id'], post['title'], post['content'], post_id))
    conn.commit()
    return jsonify(post)

@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    cursor.execute('DELETE FROM blog_posts WHERE post_id = ?', (post_id,))
    conn.commit()
    return jsonify({'message': 'Post deleted'})

@app.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    cursor.execute('SELECT * FROM comments WHERE post_id = ?', (post_id,))
    comments = cursor.fetchall()

    comments = [dict(comment) for comment in comments]
    return jsonify(comments)

@app.route('/posts/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    comment = request.get_json()
    cursor.execute('''
        INSERT INTO comments (post_id, user_id, content)
        VALUES (?, ?, ?)
    ''', (post_id, comment['user_id'], comment['content']))
    conn.commit()
    return jsonify(comment)

@app.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['GET'])
def get_comment(post_id, comment_id):
    cursor.execute('SELECT * FROM comments WHERE comment_id = ?', (comment_id,))
    comment = cursor.fetchone()

    comment = dict(comment)
    return jsonify(comment)

@app.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['PUT'])
def update_comment(post_id, comment_id):
    comment = request.get_json()
    cursor.execute('''
        UPDATE comments
        SET user_id = ?, content = ?
        WHERE comment_id = ?
    ''', (comment['user_id'], comment['content'], comment_id))
    conn.commit()
    return jsonify(comment)

@app.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(post_id, comment_id):
    cursor.execute('DELETE FROM comments WHERE comment_id = ?', (comment_id,))
    conn.commit()
    return jsonify({'message': 'Comment deleted'})


if __name__ == '__main__':
    app.run(debug=True)
