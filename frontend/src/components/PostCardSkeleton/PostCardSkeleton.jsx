import styles from './PostCardSkeleton.module.css';

export function PostCardSkeleton() {
  return (
    <article className={styles.card} aria-hidden="true">
      <div className={styles.meta}>
        <div className={`${styles.skeleton} ${styles.skeletonUsername}`} />
        <div className={`${styles.skeleton} ${styles.skeletonDot}`} />
        <div className={`${styles.skeleton} ${styles.skeletonTime}`} />
      </div>
      <div className={`${styles.skeleton} ${styles.skeletonContent}`} />
      <div className={`${styles.skeleton} ${styles.skeletonContent}`} />
      <div className={`${styles.skeleton} ${styles.skeletonContent} ${styles.short}`} />
      <div className={`${styles.skeleton} ${styles.skeletonMeta}`} />
    </article>
  );
}
