import { useState } from 'react';
import { Link } from 'react-router-dom';
import styles from './AuthForm.module.css';

/**
 * Shared auth form for login and register.
 * @param {{ mode: 'login'|'register', onSubmit: function, loading: boolean, error: string|null }} props
 */
export function AuthForm({ mode, onSubmit, loading, error }) {
  const [fields, setFields] = useState({
    username: '',
    email: '',
    password: '',
  });
  const [fieldErrors, setFieldErrors] = useState({});

  const isRegister = mode === 'register';

  function validate() {
    const errs = {};
    if (isRegister && !fields.username.trim()) {
      errs.username = 'Username is required';
    }
    if (isRegister && fields.username.trim().length > 0 && fields.username.trim().length < 3) {
      errs.username = 'Username must be at least 3 characters';
    }
    if (!fields.email.trim()) {
      errs.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(fields.email)) {
      errs.email = 'Enter a valid email address';
    }
    if (!fields.password) {
      errs.password = 'Password is required';
    } else if (isRegister && fields.password.length < 6) {
      errs.password = 'Password must be at least 6 characters';
    }
    return errs;
  }

  function handleChange(e) {
    const { name, value } = e.target;
    setFields((prev) => ({ ...prev, [name]: value }));
    if (fieldErrors[name]) {
      setFieldErrors((prev) => ({ ...prev, [name]: null }));
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length > 0) {
      setFieldErrors(errs);
      return;
    }
    const payload = isRegister
      ? { username: fields.username.trim(), email: fields.email.trim(), password: fields.password }
      : { email: fields.email.trim(), password: fields.password };
    onSubmit(payload);
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.brand}>
          <h1>Social</h1>
          <p>{isRegister ? 'Create your account' : 'Sign in to your account'}</p>
        </div>

        {error && <div className={styles.globalError} role="alert">{error}</div>}

        <form className={styles.form} onSubmit={handleSubmit} noValidate>
          {isRegister && (
            <div className={styles.field}>
              <label htmlFor="username">Username</label>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                value={fields.username}
                onChange={handleChange}
                className={fieldErrors.username ? styles.invalid : ''}
                aria-describedby={fieldErrors.username ? 'username-error' : undefined}
                aria-invalid={!!fieldErrors.username}
              />
              {fieldErrors.username && (
                <span id="username-error" className={styles.fieldError} role="alert">
                  {fieldErrors.username}
                </span>
              )}
            </div>
          )}

          <div className={styles.field}>
            <label htmlFor="email">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              value={fields.email}
              onChange={handleChange}
              className={fieldErrors.email ? styles.invalid : ''}
              aria-describedby={fieldErrors.email ? 'email-error' : undefined}
              aria-invalid={!!fieldErrors.email}
            />
            {fieldErrors.email && (
              <span id="email-error" className={styles.fieldError} role="alert">
                {fieldErrors.email}
              </span>
            )}
          </div>

          <div className={styles.field}>
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete={isRegister ? 'new-password' : 'current-password'}
              value={fields.password}
              onChange={handleChange}
              className={fieldErrors.password ? styles.invalid : ''}
              aria-describedby={fieldErrors.password ? 'password-error' : undefined}
              aria-invalid={!!fieldErrors.password}
            />
            {fieldErrors.password && (
              <span id="password-error" className={styles.fieldError} role="alert">
                {fieldErrors.password}
              </span>
            )}
          </div>

          <button
            type="submit"
            className={styles.submitBtn}
            disabled={loading}
            aria-busy={loading}
          >
            {loading ? 'Please wait...' : isRegister ? 'Create account' : 'Sign in'}
          </button>
        </form>

        <div className={styles.footer}>
          {isRegister ? (
            <>Already have an account? <Link to="/login">Sign in</Link></>
          ) : (
            <>Don&apos;t have an account? <Link to="/register">Register</Link></>
          )}
        </div>
      </div>
    </div>
  );
}
