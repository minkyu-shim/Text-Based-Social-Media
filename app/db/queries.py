from models.user import UserResponse
from models.post import PostCreate, PostResponse
from db.mongo import get_db
from bson import ObjectId

def get_all_posts():
    db = get_db
    return [db.posts.find({})]


def get_post_by_id(post_id):
    db = get_db()
    try:
        post = db.posts.find_one({'_id': ObjectId(post_id)})
        if not post:
            raise ValueError("Post not found")
        return post
    except Exception as e:
        print(f"Error: {e}")
        raise


def get_post_by_user_id(user_id):
    db = get_db()
    try:
        user_posts = [db.posts.find({'user_id': ObjectId(user_id)})]
        if not user_posts:
            raise ValueError("Post not found")
        return user_posts
    except Exception as e:
        print(f"Error: {e}")
        raise


def create_post(post: PostResponse):
    db = get_db()
    try:
        new_post = db.posts.insert_one({
            'author_id': post.author_id,
            'content': post.content,
            'timestamp': post.created_at,
            'likes_count': 0
        })
        return str(new_post.inserted_id)
    except Exception as e:
        print(f"Error creating post: {e}")
        raise


def like_post(post_id):
    db = get_db
    try:
        db.posts.update_one({'_id' : ObjectId(post_id)},
                        {'$inc' : {'likes_count' : 1}
    })
        return True
    except Exception as e:
        print(f"Error liking post {e}")
        raise


def unlike_post(post_id):
    db = get_db
    try:
        db.posts.update_one({'_id' : ObjectId(post_id)},
                        {'$inc' : {'likes_count' : -1}
    })
        return True
    except Exception as e:
        print(f"Error unliking post {e}")
        raise


def delete_post_by_id(post_id):
    db = get_db
    try:
        db.posts.delete_one({'_id' : ObjectId(post_id)})
        print(f"Post with id: {post_id} was deleted")
        return True
    except Exception as e:
        print(f"Error deleting post: {e}")
        raise