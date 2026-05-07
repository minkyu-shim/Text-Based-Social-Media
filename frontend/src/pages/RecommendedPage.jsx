import { useCallback, useState } from 'react';
import { PageTransition } from '../components/PageTransition/PageTransition';
import { PostList } from '../components/PostList/PostList';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { useFetch } from '../hooks/useFetch';
import { api } from '../api/client';

export function RecommendedPage() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const { data, loading, error, refetch } = useFetch('/feed/recommendations');
  const [likedPostIds, setLikedPostIds] = useState(new Set());
  const [localPosts, setLocalPosts] = useState(null);

  const posts = localPosts !== null ? localPosts : (data?.posts || []);

  const handleLike = useCallback(async (postId) => {
    setLikedPostIds((prev) => new Set([...prev, postId]));
    setLocalPosts((prev) => {
      const base = prev !== null ? prev : (data?.posts || []);
      return base.map((p) => p.id === postId ? { ...p, likes_count: (p.likes_count || 0) + 1 } : p);
    });
    try {
      await api.post(`/posts/${postId}/like`);
    } catch {
      setLikedPostIds((prev) => { const s = new Set(prev); s.delete(postId); return s; });
      setLocalPosts((prev) => {
        const base = prev !== null ? prev : (data?.posts || []);
        return base.map((p) => p.id === postId ? { ...p, likes_count: Math.max(0, (p.likes_count || 1) - 1) } : p);
      });
      showToast('Failed to like post', 'error');
    }
  }, [data, showToast]);

  const handleUnlike = useCallback(async (postId) => {
    setLikedPostIds((prev) => { const s = new Set(prev); s.delete(postId); return s; });
    setLocalPosts((prev) => {
      const base = prev !== null ? prev : (data?.posts || []);
      return base.map((p) => p.id === postId ? { ...p, likes_count: Math.max(0, (p.likes_count || 1) - 1) } : p);
    });
    try {
      await api.delete(`/posts/${postId}/like`);
    } catch {
      setLikedPostIds((prev) => new Set([...prev, postId]));
      setLocalPosts((prev) => {
        const base = prev !== null ? prev : (data?.posts || []);
        return base.map((p) => p.id === postId ? { ...p, likes_count: (p.likes_count || 0) + 1 } : p);
      });
      showToast('Failed to unlike post', 'error');
    }
  }, [data, showToast]);

  return (
    <PageTransition>
      <div style={{ paddingTop: '24px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#034078', marginBottom: '16px' }}>
          Recommended for you
        </h2>
        <PostList
          posts={posts}
          loading={loading}
          error={error}
          onRetry={() => { setLocalPosts(null); refetch(); }}
          emptyMessage="No recommendations available. Follow more users to see suggestions."
          currentUserId={user?.id}
          likedPostIds={likedPostIds}
          onLike={handleLike}
          onUnlike={handleUnlike}
        />
      </div>
    </PageTransition>
  );
}
