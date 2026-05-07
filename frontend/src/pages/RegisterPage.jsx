import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthForm } from '../components/AuthForm/AuthForm';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api/client';

export function RegisterPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit({ username, email, password }) {
    setLoading(true);
    setError(null);
    try {
      const data = await api.post('/auth/register', { username, email, password });
      await login(data.access_token, data.refresh_token);
      navigate('/');
    } catch (err) {
      setError(err.message || 'Registration failed. Email may already be taken.');
    } finally {
      setLoading(false);
    }
  }

  return <AuthForm mode="register" onSubmit={handleSubmit} loading={loading} error={error} />;
}
