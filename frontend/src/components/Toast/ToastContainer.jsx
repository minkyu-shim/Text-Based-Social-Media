import { useToast } from '../../contexts/ToastContext';
import styles from './Toast.module.css';

export function ToastContainer() {
  const { toasts } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className={styles.container} role="region" aria-live="polite" aria-label="Notifications">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`${styles.toast} ${styles[toast.type]} ${toast.exiting ? styles.exiting : ''}`}
          role="alert"
        >
          {toast.message}
        </div>
      ))}
    </div>
  );
}
