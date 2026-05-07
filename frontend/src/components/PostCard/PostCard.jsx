import { useState } from 'react';
import { Link } from 'react-router-dom';
import { timeAgo } from '../../utils/time';
import styles from './PostCard.module.css';

const prefersReducedMotion = () =>
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/**
 * @param {{
 *   post: { id: string, author_id: string, content: string, likes_count: number, created_at: string, author_username?: string },
 *   currentUserId: string,
 *   onLike: (postId: string) => void,
 *   onUnlike: (postId: string) => void,
 *   onDelete?: (postId: string) => void,
 *   isLiked: boolean,
 *   isNew?: boolean
 * }}
 */
export function PostCard({ post, currentUserId, onLike, onUnlike, onDelete, isLiked, isNew }) {
  const [animClass, setAnimClass] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const isOwn = post.author_id === currentUserId;

  // Derive display username: prefer author_username, fall back to truncated id
  const displayName = post.author_username
    ? `@${post.author_username}`
    : `@${String(post.author_id).slice(0, 8)}...`;

  function handleLikeClick() {
    if (isLiked) {
      setAnimClass('animateUnlike');
      onUnlike(post.id);
    } else {
      setAnimClass('animateLike');
      onLike(post.id);
    }
    // Reset animation class after it completes so it can re-trigger
    setTimeout(() => setAnimClass(null), 220);
  }

  function handleDelete() {
    if (!onDelete) return;
    if (!window.confirm('Delete this post? This cannot be undone.')) return;
    setDeleting(true);
    const delay = prefersReducedMotion() ? 0 : 350;
    setTimeout(() => onDelete(post.id), delay);
  }

  const cardClass = [
    styles.card,
    isNew ? styles.entering : '',
    deleting ? (prefersReducedMotion() ? styles.deletingInstant : styles.deleting) : '',
  ]
    .filter(Boolean)
    .join(' ');

  const iconClass = [
    styles.likeIcon,
    isLiked ? styles.liked : '',
    animClass ? styles[animClass] : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <article className={cardClass}>
      <div className={styles.meta}>
        <Link
          to={`/profile/${post.author_id}`}
          className={styles.authorLink}
          aria-label={`View profile of ${displayName}`}
        >
          {displayName}
        </Link>
        <span className={styles.dot} aria-hidden="true">·</span>
        <time
          className={styles.timestamp}
          dateTime={post.created_at}
          title={post.created_at}
        >
          {timeAgo(post.created_at)}
        </time>
      </div>

      <p className={styles.content}>{post.content}</p>

      <div className={styles.actions}>
        <button
          className={`${styles.likeBtn} ${isLiked ? styles.liked : ''}`}
          onClick={handleLikeClick}
          aria-label={isLiked ? 'Unlike post' : 'Like post'}
          aria-pressed={isLiked}
        >
          <span className={iconClass} aria-hidden="true">
            {isLiked ? '♥' : '♡'}
          </span>
          <span className={styles.likeCount}>{post.likes_count ?? 0}</span>
        </button>

        {isOwn && onDelete && (
          <button
            className={styles.deleteBtn}
            onClick={handleDelete}
            aria-label="Delete post"
            disabled={deleting}
          >
            <span aria-hidden="true">🗑</span>
          </button>
        )}
      </div>
    </article>
  );
}
