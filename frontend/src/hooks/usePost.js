import { useState } from 'react';
import { api } from '../api/client';

/**
 * Hook for creating a new post.
 * @returns {{ submit, loading, error }}
 */
export function usePost() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function submit(content) {
    setLoading(true);
    setError(null);
    try {
      const post = await api.post('/posts/', { content });
      return post;
    } catch (err) {
      setError(err.message || 'Failed to create post');
      return null;
    } finally {
      setLoading(false);
    }
  }

  return { submit, loading, error };
}
