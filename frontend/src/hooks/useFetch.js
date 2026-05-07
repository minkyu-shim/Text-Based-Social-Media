import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from '../api/client';

/**
 * Generic GET fetcher.
 * @param {string|null} url - the path to fetch; pass null to skip fetching
 * @returns {{ data, loading, error, refetch }}
 */
export function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(!!url);
  const [error, setError] = useState(null);
  const urlRef = useRef(url);
  urlRef.current = url;

  const fetchData = useCallback(async (path) => {
    if (!path) return;
    setLoading(true);
    setError(null);
    try {
      const result = await api.get(path);
      setData(result);
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (url) fetchData(url);
    else {
      setData(null);
      setLoading(false);
      setError(null);
    }
  }, [url, fetchData]);

  const refetch = useCallback(() => fetchData(urlRef.current), [fetchData]);

  return { data, loading, error, refetch };
}
