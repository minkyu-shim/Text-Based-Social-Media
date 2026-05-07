import { useState } from 'react';
import { api } from '../api/client';

/**
 * Manages follow/unfollow state for a target user.
 * Initial state is unknown (false) — only tracks changes made in this session.
 * @param {string} userId - target user's ID
 * @param {boolean} initialFollowing - seed value if known
 * @returns {{ isFollowing, follow, unfollow, loading, error }}
 */
export function useFollow(userId, initialFollowing = false) {
  const [isFollowing, setIsFollowing] = useState(initialFollowing);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function follow() {
    setLoading(true);
    setError(null);
    // Optimistic update
    setIsFollowing(true);
    try {
      await api.post(`/users/${userId}/follow`);
    } catch (err) {
      setIsFollowing(false);
      setError(err.message || 'Failed to follow');
      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function unfollow() {
    setLoading(true);
    setError(null);
    // Optimistic update
    setIsFollowing(false);
    try {
      await api.delete(`/users/${userId}/follow`);
    } catch (err) {
      setIsFollowing(true);
      setError(err.message || 'Failed to unfollow');
      throw err;
    } finally {
      setLoading(false);
    }
  }

  return { isFollowing, follow, unfollow, loading, error };
}
