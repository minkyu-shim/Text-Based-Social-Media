import { useCallback, useState } from 'react';
import { EditProfileForm } from '../components/EditProfileForm/EditProfileForm';
import { PageTransition } from '../components/PageTransition/PageTransition';
import { PostList } from '../components/PostList/PostList';
import { ProfileHeader } from '../components/ProfileHeader/ProfileHeader';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { useFetch } from '../hooks/useFetch';
import { api } from '../api/client';

export function MyProfilePage() {
  const { user, updateUser } = useAuth();
  const { showToast } = useToast();
  const [showEdit, setShowEdit] = useState(false);
  const [likedPostIds, setLikedPostIds] = useState(new Set());
  const [localPosts, setLocalPosts] = useState(null);

  const userId = user?.id;
  const { data: postsData, loading, error, refetch } = useFetch(
    userId ? `/posts/by/${userId}` : null
  );

  const posts = localPosts !== null ? localPosts : (Array.isArray(postsData) ? postsData : []);

  function handleSaved(updatedUser) {
    updateUser(updatedUser);
    setShowEdit(false);
  }

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

  const handleDelete = useCallback(async (postId) => {
    try {
      await api.delete(`/posts/${postId}`);
      setLocalPosts((prev) => {
        const base = prev !== null ? prev : (Array.isArray(postsData) ? postsData : []);
        return base.filter((p) => p.id !== postId);
      });
      showToast('Post deleted', 'success');
    } catch (err) {
      showToast(err.message || 'Failed to delete post', 'error');
    }
  }, [postsData, showToast]);

  return (
    <PageTransition>
      <div style={{ paddingTop: '8px' }}>
        <ProfileHeader
          user={user}
          showEditButton={!showEdit}
          onEditClick={() => setShowEdit(true)}
        />

        {showEdit && (
          <EditProfileForm
            user={user}
            onSaved={handleSaved}
            onCancel={() => setShowEdit(false)}
          />
        )}

        <PostList
          posts={posts}
          loading={loading}
          error={error}
          onRetry={() => { setLocalPosts(null); refetch(); }}
          emptyMessage="You haven't posted anything yet."
          currentUserId={userId}
          likedPostIds={likedPostIds}
          onLike={handleLike}
          onUnlike={handleUnlike}
          onDelete={handleDelete}
        />
      </div>
    </PageTransition>
  );
}
