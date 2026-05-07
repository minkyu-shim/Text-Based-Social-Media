import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthForm } from '../components/AuthForm/AuthForm';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api/client';

export function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit({ email, password }) {
    setLoading(true);
    setError(null);
    try {
      const data = await api.post('/auth/login', { email, password });
      await login(data.access_token, data.refresh_token);
      navigate('/');
    } catch (err) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  }

  return <AuthForm mode="login" onSubmit={handleSubmit} loading={loading} error={error} />;
}
