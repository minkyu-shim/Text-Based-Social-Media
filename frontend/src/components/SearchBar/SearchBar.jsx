import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './SearchBar.module.css';

/**
 * @param {{ initialQuery?: string }} props
 */
export function SearchBar({ initialQuery = '' }) {
  const [query, setQuery] = useState(initialQuery);
  const navigate = useNavigate();

  function handleSubmit(e) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    navigate(`/search?q=${encodeURIComponent(q)}`);
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit} role="search">
      <input
        type="search"
        className={styles.input}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search posts..."
        aria-label="Search posts"
      />
      <button
        type="submit"
        className={styles.btn}
        disabled={!query.trim()}
        aria-label="Search"
      >
        Search
      </button>
    </form>
  );
}
