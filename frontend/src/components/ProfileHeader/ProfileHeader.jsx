import { formatMonthYear } from '../../utils/time';
import styles from './ProfileHeader.module.css';

/**
 * @param {{
 *   user: { id: string, username: string, email?: string, bio?: string, first_name?: string, last_name?: string, created_at?: string },
 *   showEditButton?: boolean,
 *   onEditClick?: function
 * }}
 */
export function ProfileHeader({ user, showEditButton, onEditClick }) {
  if (!user) return null;

  const displayName = [user.first_name, user.last_name].filter(Boolean).join(' ') || user.username;

  return (
    <header className={styles.header}>
      <h1 className={styles.displayName}>{displayName}</h1>
      <p className={styles.handle}>@{user.username}</p>
      {user.email && <p className={styles.email}>{user.email}</p>}
      {user.bio && <p className={styles.bio}>{user.bio}</p>}
      {user.created_at && (
        <p className={styles.joined}>Joined {formatMonthYear(user.created_at)}</p>
      )}
      {showEditButton && (
        <button className={styles.editBtn} onClick={onEditClick} aria-label="Edit profile">
          Edit profile
        </button>
      )}
    </header>
  );
}
