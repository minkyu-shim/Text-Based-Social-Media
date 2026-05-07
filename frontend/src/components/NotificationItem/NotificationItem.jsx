import { timeAgo } from '../../utils/time';
import styles from './NotificationItem.module.css';

const TYPE_ICONS = {
  like: '♥',
  follow: '◎',
  mention: '@',
  default: '•',
};

/**
 * @param {{ notification: { type?: string, message?: string, created_at?: string, data?: object } }}
 */
export function NotificationItem({ notification }) {
  const icon = TYPE_ICONS[notification.type] || TYPE_ICONS.default;

  // Build a human-readable message from the notification payload
  let message = notification.message;
  if (!message) {
    if (notification.type === 'like') {
      const who = notification.data?.username || notification.data?.user_id || 'Someone';
      message = `${who} liked your post`;
    } else if (notification.type === 'follow') {
      const who = notification.data?.username || notification.data?.user_id || 'Someone';
      message = `${who} started following you`;
    } else {
      message = JSON.stringify(notification);
    }
  }

  return (
    <li className={styles.item}>
      <span className={styles.icon} aria-hidden="true">{icon}</span>
      <div className={styles.body}>
        <p className={styles.message}>{message}</p>
        {notification.created_at && (
          <time className={styles.time} dateTime={notification.created_at}>
            {timeAgo(notification.created_at)}
          </time>
        )}
      </div>
    </li>
  );
}
