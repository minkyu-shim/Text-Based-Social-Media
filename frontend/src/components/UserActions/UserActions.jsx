import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import styles from './UserActions.module.css';

const prefersReducedMotion = () =>
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/**
 * @param {{ targetUser: { id: string, username: string } }} props
 */
export function UserActions({ targetUser }) {
  const { user: currentUser } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [isFollowing, setIsFollowing] = useState(false);
  const [isCloseFriend, setIsCloseFriend] = useState(false);
  const [isBlocked, setIsBlocked] = useState(false);
  const [hopDistance, setHopDistance] = useState(null);
  const [loadingAction, setLoadingAction] = useState(null); // 'follow'|'closefriend'|'block'

  useEffect(() => {
    if (!currentUser || !targetUser) return;
    // Fetch hop distance
    api
      .get(`/users/${currentUser.id}/distance/${targetUser.id}`)
      .then((data) => {
        if (data && data.connected) setHopDistance(data.distance);
        else setHopDistance(null);
      })
      .catch(() => setHopDistance(null));
  }, [currentUser, targetUser]);

  async function handleFollow() {
    setLoadingAction('follow');
    const wasFollowing = isFollowing;
    setIsFollowing(!wasFollowing);
    try {
      if (wasFollowing) {
        await api.delete(`/users/${targetUser.id}/follow`);
        showToast(`Unfollowed @${targetUser.username}`, 'success');
      } else {
        await api.post(`/users/${targetUser.id}/follow`);
        showToast(`Following @${targetUser.username}`, 'success');
      }
    } catch (err) {
      setIsFollowing(wasFollowing);
      showToast(err.message || 'Action failed', 'error');
    } finally {
      setLoadingAction(null);
    }
  }

  async function handleCloseFriend() {
    if (!isFollowing) return;
    setLoadingAction('closefriend');
    const wasClose = isCloseFriend;
    setIsCloseFriend(!wasClose);
    try {
      if (wasClose) {
        await api.delete(`/users/${targetUser.id}/close-friends`);
        showToast('Removed from close friends', 'success');
      } else {
        await api.post(`/users/${targetUser.id}/close-friends`);
        showToast('Added to close friends', 'success');
      }
    } catch (err) {
      setIsCloseFriend(wasClose);
      showToast(err.message || 'Action failed', 'error');
    } finally {
      setLoadingAction(null);
    }
  }

  async function handleBlock() {
    if (isBlocked) {
      // Unblock
      setLoadingAction('block');
      try {
        await api.delete(`/users/${targetUser.id}/block`);
        setIsBlocked(false);
        showToast(`Unblocked @${targetUser.username}`, 'success');
      } catch (err) {
        showToast(err.message || 'Failed to unblock', 'error');
      } finally {
        setLoadingAction(null);
      }
      return;
    }

    if (!window.confirm(`Block @${targetUser.username}? They will no longer appear in your feed.`)) {
      return;
    }

    setLoadingAction('block');
    setIsBlocked(true);

    const delay = prefersReducedMotion() ? 0 : 350;
    setTimeout(async () => {
      try {
        await api.post(`/users/${targetUser.id}/block`);
        showToast(`Blocked @${targetUser.username}`, 'error');
        navigate('/');
      } catch (err) {
        setIsBlocked(false);
        showToast(err.message || 'Failed to block', 'error');
      } finally {
        setLoadingAction(null);
      }
    }, delay);
  }

  if (!currentUser) return null;

  return (
    <div className={styles.actions}>
      {/* Follow / Unfollow */}
      <button
        className={`${styles.followBtn} ${isFollowing ? styles.following : ''}`}
        onClick={handleFollow}
        disabled={loadingAction === 'follow'}
        aria-label={isFollowing ? 'Unfollow user' : 'Follow user'}
        aria-pressed={isFollowing}
      >
        <span className={styles.labelWrap} aria-hidden="true">
          <span className={`${styles.label} ${styles.labelFollow}`}>Follow</span>
          <span className={`${styles.label} ${styles.labelFollowing}`}>Following</span>
        </span>
        {/* Accessible text (hidden visually but read by screen readers) */}
        <span className="sr-only">{isFollowing ? 'Following' : 'Follow'}</span>
      </button>

      {/* Close Friend */}
      <button
        className={`${styles.closeFriendBtn} ${isCloseFriend ? styles.active : ''}`}
        onClick={handleCloseFriend}
        disabled={!isFollowing || loadingAction === 'closefriend'}
        aria-label={isCloseFriend ? 'Remove from close friends' : 'Add to close friends'}
        aria-pressed={isCloseFriend}
        title={!isFollowing ? 'Follow this user first' : undefined}
      >
        {isCloseFriend ? 'Close Friend ✓' : 'Close Friend'}
      </button>

      {/* Block */}
      <button
        className={`${styles.blockBtn} ${isBlocked ? styles.blocked : ''}`}
        onClick={handleBlock}
        disabled={loadingAction === 'block'}
        aria-label={isBlocked ? 'Unblock user' : 'Block user'}
      >
        {isBlocked ? 'Unblock' : 'Block'}
      </button>

      {/* Hop distance */}
      {hopDistance !== null && (
        <p className={styles.hopDistance}>
          Hop distance from you: <strong>{hopDistance} {hopDistance === 1 ? 'hop' : 'hops'}</strong>
        </p>
      )}
      {hopDistance === null && currentUser.id !== targetUser.id && (
        <p className={styles.hopDistance}>No connection found</p>
      )}
    </div>
  );
}
