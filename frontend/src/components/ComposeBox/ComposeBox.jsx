import { useState } from 'react';
import { usePost } from '../../hooks/usePost';
import { useToast } from '../../contexts/ToastContext';
import styles from './ComposeBox.module.css';

const MAX_CHARS = 280;

/**
 * @param {{ onPosted: (post: object) => void }} props
 */
export function ComposeBox({ onPosted }) {
  const [content, setContent] = useState('');
  const { submit, loading, error } = usePost();
  const { showToast } = useToast();

  const remaining = MAX_CHARS - content.length;
  const isNearLimit = remaining <= 30;
  const canPost = content.trim().length > 0 && remaining >= 0 && !loading;

  async function handleSubmit(e) {
    e.preventDefault();
    if (!canPost) return;

    const post = await submit(content.trim());
    if (post) {
      setContent('');
      showToast('Posted!', 'success');
      onPosted && onPosted(post);
    } else {
      showToast('Failed to post. Please try again.', 'error');
    }
  }

  return (
    <div className={styles.box}>
      <form onSubmit={handleSubmit}>
        <textarea
          className={styles.textarea}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="What's on your mind?"
          maxLength={MAX_CHARS}
          aria-label="Compose a new post"
          rows={3}
        />
        <div className={styles.footer}>
          <span className={`${styles.charCount} ${isNearLimit ? styles.nearLimit : ''}`}>
            {remaining}/{MAX_CHARS}
          </span>
          <button
            type="submit"
            className={styles.postBtn}
            disabled={!canPost}
            aria-label="Post"
          >
            {loading ? 'Posting...' : 'Post'}
          </button>
        </div>
        {error && <p className={styles.error} role="alert">{error}</p>}
      </form>
    </div>
  );
}
