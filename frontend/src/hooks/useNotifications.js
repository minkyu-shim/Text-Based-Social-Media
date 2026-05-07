import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from '../api/client';

const POLL_INTERVAL = 30000; // 30 seconds

/**
 * Fetches notifications and polls every 30s.
 * Pauses when the tab is hidden.
 * @returns {{ notifications, count, loading, error, refetch }}
 */
export function useNotifications() {
  const [notifications, setNotifications] = useState([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  const fetchNotifications = useCallback(async () => {
    if (document.visibilityState === 'hidden') return;
    try {
      const data = await api.get('/notifications/');
      if (data) {
        setNotifications(data.notifications || []);
        setCount(data.count || 0);
        setError(null);
      }
    } catch (err) {
      setError(err.message || 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();

    intervalRef.current = setInterval(fetchNotifications, POLL_INTERVAL);

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        fetchNotifications();
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      clearInterval(intervalRef.current);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [fetchNotifications]);

  return { notifications, count, loading, error, refetch: fetchNotifications };
}
