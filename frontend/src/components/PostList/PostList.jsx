import { PostCard } from '../PostCard/PostCard';
import { PostCardSkeleton } from '../PostCardSkeleton/PostCardSkeleton';
import styles from './PostList.module.css';

/**
 * @param {{
 *   posts: Array,
 *   loading: boolean,
 *   error: string|null,
 *   onRetry: function,
 *   emptyMessage: string,
 *   currentUserId: string,
 *   likedPostIds: Set<string>,
 *   onLike: function,
 *   onUnlike: function,
 *   onDelete?: function,
 *   newPostId?: string
 * }}
 */
export function PostList({
  posts,
  loading,
  error,
  onRetry,
  emptyMessage = 'No posts yet.',
  currentUserId,
  likedPostIds,
  onLike,
  onUnlike,
  onDelete,
  newPostId,
}) {
  if (loading) {
    return (
      <div className={styles.list} aria-busy="true" aria-label="Loading posts">
        {[1, 2, 3, 4].map((n) => (
          <PostCardSkeleton key={n} />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorBox} role="alert">
        <p>{error}</p>
        {onRetry && (
          <button className={styles.retryBtn} onClick={onRetry}>
            Try again
          </button>
        )}
      </div>
    );
  }

  if (!posts || posts.length === 0) {
    return (
      <div className={styles.empty} role="status">
        <p>{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className={styles.list}>
      {posts.map((post) => (
        <PostCard
          key={post.id}
          post={post}
          currentUserId={currentUserId}
          isLiked={likedPostIds ? likedPostIds.has(post.id) : false}
          onLike={onLike}
          onUnlike={onUnlike}
          onDelete={onDelete}
          isNew={post.id === newPostId}
        />
      ))}
    </div>
  );
}
