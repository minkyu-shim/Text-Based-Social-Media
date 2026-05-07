import { useCallback, useState } from 'react';
import { ComposeBox } from '../components/ComposeBox/ComposeBox';
import { PageTransition } from '../components/PageTransition/PageTransition';
import { PostList } from '../components/PostList/PostList';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { useFetch } from '../hooks/useFetch';
import { api } from '../api/client';

export function HomeFeedPage() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const { data, loading, error, refetch } = useFetch('/feed/?limit=20');
  const [localPosts, setLocalPosts] = useState(null);
  const [likedPostIds, setLikedPostIds] = useState(new Set());
  const [newPostId, setNewPostId] = useState(null);

  // Use local posts if set, otherwise use data from API
  const posts = localPosts !== null ? localPosts : (data?.posts || []);

  function handlePosted(post) {
    const enriched = {
      ...post,
      author_username: user?.username,
    };
    const currentPosts = localPosts !== null ? localPosts : (data?.posts || []);
    setLocalPosts([enriched, ...currentPosts]);
    setNewPostId(enriched.id);
    // Clear the "new" flag after the animation
    setTimeout(() => setNewPostId(null), 400);
  }

  const handleLike = useCallback(async (postId) => {
    // Optimistic update
    setLikedPostIds((prev) => {
      const next = new Set(prev);
      next.add(postId);
      return next;
    });
    setLocalPosts((prev) => {
      const base = prev !== null ? prev : (data?.posts || []);
      return base.map((p) =>
        p.id === postId ? { ...p, likes_count: (p.likes_count || 0) + 1 } : p
      );
    });
    try {
      await api.post(`/posts/${postId}/like`);
    } catch (err) {
      // Rollback
      setLikedPostIds((prev) => {
        const next = new Set(prev);
        next.delete(postId);
        return next;
      });
      setLocalPosts((prev) => {
        const base = prev !== null ? prev : (data?.posts || []);
        return base.map((p) =>
          p.id === postId ? { ...p, likes_count: Math.max(0, (p.likes_count || 1) - 1) } : p
        );
      });
      showToast('Failed to like post', 'error');
    }
  }, [data, showToast]);

  const handleUnlike = useCallback(async (postId) => {
    // Optimistic update
    setLikedPostIds((prev) => {
      const next = new Set(prev);
      next.delete(postId);
      return next;
    });
    setLocalPosts((prev) => {
      const base = prev !== null ? prev : (data?.posts || []);
      return base.map((p) =>
        p.id === postId ? { ...p, likes_count: Math.max(0, (p.likes_count || 1) - 1) } : p
      );
    });
    try {
      await api.delete(`/posts/${postId}/like`);
    } catch (err) {
      // Rollback
      setLikedPostIds((prev) => {
        const next = new Set(prev);
        next.add(postId);
        return next;
      });
      setLocalPosts((prev) => {
        const base = prev !== null ? prev : (data?.posts || []);
        return base.map((p) =>
          p.id === postId ? { ...p, likes_count: (p.likes_count || 0) + 1 } : p
        );
      });
      showToast('Failed to unlike post', 'error');
    }
  }, [data, showToast]);

  const handleDelete = useCallback(async (postId) => {
    try {
      await api.delete(`/posts/${postId}`);
      setLocalPosts((prev) => {
        const base = prev !== null ? prev : (data?.posts || []);
        return base.filter((p) => p.id !== postId);
      });
      showToast('Post deleted', 'success');
    } catch (err) {
      showToast(err.message || 'Failed to delete post', 'error');
    }
  }, [data, showToast]);

  function handleRetry() {
    setLocalPosts(null);
    refetch();
  }

  return (
    <PageTransition>
      <ComposeBox onPosted={handlePosted} />
      <PostList
        posts={posts}
        loading={loading}
        error={error}
        onRetry={handleRetry}
        emptyMessage="You're not following anyone yet. Explore recommendations."
        currentUserId={user?.id}
        likedPostIds={likedPostIds}
        onLike={handleLike}
        onUnlike={handleUnlike}
        onDelete={handleDelete}
        newPostId={newPostId}
      />
    </PageTransition>
  );
}
