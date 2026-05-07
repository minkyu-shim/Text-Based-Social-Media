import { useState } from 'react';
import { api } from '../../api/client';
import { useToast } from '../../contexts/ToastContext';
import styles from './EditProfileForm.module.css';

/**
 * @param {{
 *   user: object,
 *   onSaved: (updatedUser: object) => void,
 *   onCancel: function
 * }}
 */
export function EditProfileForm({ user, onSaved, onCancel }) {
  const [fields, setFields] = useState({
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    bio: user.bio || '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { showToast } = useToast();

  function handleChange(e) {
    const { name, value } = e.target;
    setFields((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Only send non-empty changed fields
    const updates = {};
    if (fields.first_name.trim()) updates.first_name = fields.first_name.trim();
    if (fields.last_name.trim()) updates.last_name = fields.last_name.trim();
    if (fields.bio !== (user.bio || '')) updates.bio = fields.bio.trim();

    if (Object.keys(updates).length === 0) {
      onCancel();
      return;
    }

    try {
      const updated = await api.patch('/users/me', updates);
      showToast('Profile updated!', 'success');
      onSaved(updated);
    } catch (err) {
      setError(err.message || 'Failed to update profile');
      showToast('Failed to update profile', 'error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.form}>
      <p className={styles.title}>Edit Profile</p>
      <form onSubmit={handleSubmit}>
        <div className={styles.fields}>
          <div className={styles.field}>
            <label htmlFor="first_name">First name</label>
            <input
              id="first_name"
              name="first_name"
              type="text"
              value={fields.first_name}
              onChange={handleChange}
              autoComplete="given-name"
            />
          </div>
          <div className={styles.field}>
            <label htmlFor="last_name">Last name</label>
            <input
              id="last_name"
              name="last_name"
              type="text"
              value={fields.last_name}
              onChange={handleChange}
              autoComplete="family-name"
            />
          </div>
          <div className={styles.field}>
            <label htmlFor="bio">Bio</label>
            <textarea
              id="bio"
              name="bio"
              value={fields.bio}
              onChange={handleChange}
              placeholder="Tell people about yourself..."
              rows={3}
            />
          </div>
        </div>

        {error && <p className={styles.error} role="alert">{error}</p>}

        <div className={styles.actions}>
          <button type="submit" className={styles.saveBtn} disabled={loading}>
            {loading ? 'Saving...' : 'Save'}
          </button>
          <button
            type="button"
            className={styles.cancelBtn}
            onClick={onCancel}
            disabled={loading}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
