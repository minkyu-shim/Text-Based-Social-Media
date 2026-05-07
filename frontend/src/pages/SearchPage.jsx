import { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { PageTransition } from '../components/PageTransition/PageTransition';
import { PostList } from '../components/PostList/PostList';
import { SearchBar } from '../components/SearchBar/SearchBar';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { api } from '../api/client';

export function SearchPage() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';

  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [likedPostIds, setLikedPostIds] = useState(new Set());

  useEffect(() => {
    if (!query) {
      setPosts([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    api
      .get(`/feed/search?q=${encodeURIComponent(query)}`)
      .then((data) => {
        setPosts(data?.posts || []);
      })
      .catch((err) => {
        setError(err.message || 'Search failed');
      })
      .finally(() => setLoading(false));
  }, [query]);

  const handleLike = useCallback(async (postId) => {
    setLikedPostIds((prev) => new Set([...prev, postId]));
    setPosts((prev) =>
      prev.map((p) => p.id === postId ? { ...p, likes_count: (p.likes_count || 0) + 1 } : p)
    );
    try {
      await api.post(`/posts/${postId}/like`);
    } catch {
      setLikedPostIds((prev) => { const s = new Set(prev); s.delete(postId); return s; });
      setPosts((prev) =>
        prev.map((p) => p.id === postId ? { ...p, likes_count: Math.max(0, (p.likes_count || 1) - 1) } : p)
      );
      showToast('Failed to like post', 'error');
    }
  }, [showToast]);

  const handleUnlike = useCallback(async (postId) => {
    setLikedPostIds((prev) => { const s = new Set(prev); s.delete(postId); return s; });
    setPosts((prev) =>
      prev.map((p) => p.id === postId ? { ...p, likes_count: Math.max(0, (p.likes_count || 1) - 1) } : p)
    );
    try {
      await api.delete(`/posts/${postId}/like`);
    } catch {
      setLikedPostIds((prev) => new Set([...prev, postId]));
      setPosts((prev) =>
        prev.map((p) => p.id === postId ? { ...p, likes_count: (p.likes_count || 0) + 1 } : p)
      );
      showToast('Failed to unlike post', 'error');
    }
  }, [showToast]);

  const resultLine = query && !loading && !error
    ? `${posts.length} result${posts.length !== 1 ? 's' : ''} for "${query}"`
    : null;

  return (
    <PageTransition>
      <div style={{ paddingTop: '24px' }}>
        <SearchBar initialQuery={query} />
        {resultLine && (
          <p style={{ fontSize: '14px', color: '#666666', marginBottom: '8px', fontFamily: "'IBM Plex Mono', monospace" }}>
            {resultLine}
          </p>
        )}
        <PostList
          posts={posts}
          loading={loading}
          error={error}
          onRetry={() => {}}
          emptyMessage={query ? `No posts matched "${query}".` : 'Enter a query to search posts.'}
          currentUserId={user?.id}
          likedPostIds={likedPostIds}
          onLike={handleLike}
          onUnlike={handleUnlike}
        />
      </div>
    </PageTransition>
  );
}
