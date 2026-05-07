import { useEffect, useRef, useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useNotifications } from '../../hooks/useNotifications';
import styles from './Sidebar.module.css';

function NotificationBadge({ count }) {
  const [popping, setPopping] = useState(false);
  const prevCount = useRef(0);

  useEffect(() => {
    if (count > 0 && prevCount.current === 0) {
      setPopping(true);
      const t = setTimeout(() => setPopping(false), 250);
      return () => clearTimeout(t);
    }
    prevCount.current = count;
  }, [count]);

  if (!count) return null;

  return (
    <span
      className={`${styles.badge} ${popping ? styles.popping : ''}`}
      aria-label={`${count} notifications`}
    >
      {count > 99 ? '99+' : count}
    </span>
  );
}

export function Sidebar() {
  const { user, logout } = useAuth();
  const { count } = useNotifications();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate('/login');
  }

  const navItems = [
    { to: '/', label: 'Home', icon: '⌂', exact: true },
    { to: '/search', label: 'Search', icon: '⌕' },
    { to: '/recommendations', label: 'Explore', icon: '✦' },
    { to: '/notifications', label: 'Notifications', icon: '♪', badge: count },
    { to: '/profile/me', label: 'Profile', icon: '◉' },
  ];

  return (
    <nav className={styles.sidebar} aria-label="Main navigation">
      <Link to="/" className={styles.logo}>
        Social
      </Link>

      <div className={styles.nav}>
        {navItems.map(({ to, label, icon, exact, badge }) => (
          <NavLink
            key={to}
            to={to}
            end={exact}
            className={({ isActive }) =>
              `${styles.navLink} ${isActive ? styles.active : ''}`
            }
            aria-label={label}
          >
            <span className={styles.badgeWrapper}>
              <span className={styles.navIcon} aria-hidden="true">{icon}</span>
              {badge > 0 && <NotificationBadge count={badge} />}
            </span>
            <span className={styles.navLabel}>{label}</span>
          </NavLink>
        ))}
      </div>

      <div className={styles.bottom}>
        {user && (
          <div className={styles.userInfo}>
            <div>
              <div className={styles.userName}>
                {user.first_name || user.username}
              </div>
              <div className={styles.userHandle}>@{user.username}</div>
            </div>
          </div>
        )}
        <button
          className={styles.logoutBtn}
          onClick={handleLogout}
          aria-label="Log out"
        >
          <span aria-hidden="true">⏻</span>
          Log out
        </button>
      </div>
    </nav>
  );
}
