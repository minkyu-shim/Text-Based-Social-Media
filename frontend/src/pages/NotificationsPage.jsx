import { PageTransition } from '../components/PageTransition/PageTransition';
import { NotificationItem } from '../components/NotificationItem/NotificationItem';
import { useNotifications } from '../hooks/useNotifications';
import styles from './NotificationsPage.module.css';

export function NotificationsPage() {
  const { notifications, loading, error, refetch } = useNotifications();

  return (
    <PageTransition>
      <div className={styles.page}>
        <h1 className={styles.title}>Notifications</h1>

        {loading && (
          <p className={styles.status}>Loading notifications...</p>
        )}

        {error && !loading && (
          <div className={styles.error} role="alert">
            <p>{error}</p>
            <button className={styles.retryBtn} onClick={refetch}>Try again</button>
          </div>
        )}

        {!loading && !error && notifications.length === 0 && (
          <p className={styles.empty}>No notifications yet.</p>
        )}

        {notifications.length > 0 && (
          <ul className={styles.list} aria-label="Notifications list">
            {notifications.map((n, i) => (
              <NotificationItem key={n.id || `notif-${i}`} notification={n} />
            ))}
          </ul>
        )}
      </div>
    </PageTransition>
  );
}
