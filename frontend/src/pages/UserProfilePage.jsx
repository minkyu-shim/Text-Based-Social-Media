import { useCallback, useState } from 'react';
import { useParams } from 'react-router-dom';
import { PageTransition } from '../components/PageTransition/PageTransition';
import { PostList } from '../components/PostList/PostList';
import { ProfileHeader } from '../components/ProfileHeader/ProfileHeader';
import { UserActions } from '../components/UserActions/UserActions';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { useFetch } from '../hooks/useFetch';
import { api } from '../api/client';
import styles from './UserProfilePage.module.css';

export function UserProfilePage() {
  const { userId } = useParams();
  const { user: currentUser } = useAuth();
  const { showToast } = useToast();

  const [likedPostIds, setLikedPostIds] = useState(new Set());
  const [localPosts, setLocalPosts] = useState(null);

  const { data: profileData, loading: profileLoading, error: profileError } = useFetch(
    userId ? `/users/${userId}` : null
  );
  const { data: postsData, loading: postsLoading, error: postsError, refetch } = useFetch(
    userId ? `/posts/by/${userId}` : null
  );

  const posts = localPosts !== null ? localPosts : (Array.isArray(postsData) ? postsData : []);

  // If this is the current user's own profile, redirect to /profile/me
  const isSelf = currentUser && userId === currentUser.id;

  const handleLike = useCallback(async (postId) => {
    setLikedPostIds((prev) => new Set([...prev, postId]));
    setLocalPosts((prev) => {
      const base = prev !== null ? prev : (Array.isArray(postsData) ? postsData : []);
      return base.map((p) => p.id === postId ? { ...p, likes_count: (p.likes_count || 0) + 1 } : p);
    });
    try {
      await api.post(`/posts/${postId}/like`);
    } catch {
      setLikedPostIds((prev) => { const s = new Set(prev); s.delete(postId); return s; });
      setLocalPosts((prev) => {
        const base = prev !== null ? prev : (Array.isArray(postsData) ? postsData : []);
        return base.map((p) => p.id === postId ? { ...p, likes_count: Math.max(0, (p.likes_count || 1) - 1) } : p);
      });
      showToast('Failed to like post', 'error');
    }
  }, [postsData, showToast]);

  const handleUnlike = useCallback(async (postId) => {
    setLikedPostIds((prev) => { const s = new Set(prev); s.delete(postId); return s; });
    setLocalPosts((prev) => {
      const base = prev !== null ? prev : (Array.isArray(postsData) ? postsData : []);
      return base.map((p) => p.id === postId ? { ...p, likes_count: Math.max(0, (p.likes_count || 1) - 1) } : p);
    });
    try {
      await api.delete(`/posts/${postId}/like`);
    } catch {
      setLikedPostIds((prev) => new Set([...prev, postId]));
      setLocalPosts((prev) => {
        const base = prev !== null ? prev : (Array.isArray(postsData) ? postsData : []);
        return base.map((p) => p.id === postId ? { ...p, likes_count: (p.likes_count || 0) + 1 } : p);
      });
      showToast('Failed to unlike post', 'error');
    }
  }, [postsData, showToast]);

  if (profileLoading) {
    return (
      <PageTransition>
        <div className={styles.page}>
          <p className={styles.status}>Loading profile...</p>
        </div>
      </PageTransition>
    );
  }

  if (profileError) {
    return (
      <PageTransition>
        <div className={styles.page}>
          <p className={styles.errorMsg} role="alert">{profileError}</p>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className={styles.page}>
        <ProfileHeader user={profileData} />

        {!isSelf && profileData && (
          <UserActions targetUser={profileData} />
        )}

        <PostList
          posts={posts}
          loading={postsLoading}
          error={postsError}
          onRetry={() => { setLocalPosts(null); refetch(); }}
          emptyMessage="This user hasn't posted anything yet."
          currentUserId={currentUser?.id}
          likedPostIds={likedPostIds}
          onLike={handleLike}
          onUnlike={handleUnlike}
        />
      </div>
    </PageTransition>
  );
}
