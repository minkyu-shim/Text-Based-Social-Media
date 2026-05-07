import { useEffect, useRef, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useNotifications } from '../../hooks/useNotifications';
import styles from './BottomNav.module.css';

function BottomBadge({ count }) {
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
    <span className={`${styles.badge} ${popping ? styles.popping : ''}`}>
      {count > 99 ? '99+' : count}
    </span>
  );
}

export function BottomNav() {
  const { count } = useNotifications();

  const navItems = [
    { to: '/', label: 'Home', icon: '⌂', exact: true },
    { to: '/search', label: 'Search', icon: '⌕' },
    { to: '/recommendations', label: 'Explore', icon: '✦' },
    { to: '/notifications', label: 'Notifs', icon: '♪', badge: count },
    { to: '/profile/me', label: 'Profile', icon: '◉' },
  ];

  return (
    <nav className={styles.bottomNav} aria-label="Mobile navigation">
      {navItems.map(({ to, label, icon, exact, badge }) => (
        <NavLink
          key={to}
          to={to}
          end={exact}
          className={({ isActive }) =>
            `${styles.navItem} ${isActive ? styles.active : ''}`
          }
          aria-label={label}
        >
          <span className={styles.badgeWrapper}>
            <span className={styles.navIcon} aria-hidden="true">{icon}</span>
            {badge > 0 && <BottomBadge count={badge} />}
          </span>
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
