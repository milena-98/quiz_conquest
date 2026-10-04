import { useEffect, useState } from 'react'
import './App.css'

const avatarOptions = ['knight-1', 'knight-2', 'knight-3', 'knight-4']

const getCsrfToken = () => {
  const value = document.cookie
    .split('; ')
    .find((item) => item.startsWith('csrftoken='))

  return value ? value.split('=')[1] : ''
}

const formatErrors = (value) => {
  if (Array.isArray(value)) {
    return value.join(', ')
  }

  if (value && typeof value === 'object') {
    return Object.values(value)
      .flatMap((item) => formatErrors(item).split(', '))
      .filter(Boolean)
      .join(', ')
  }

  return String(value)
}

const apiRequest = async (url, options = {}) => {
  const headers = { ...(options.headers || {}) }

  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  if (options.method && options.method !== 'GET' && options.method !== 'HEAD') {
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken
    }
  }

  const response = await fetch(url, {
    ...options,
    credentials: 'include',
    headers,
  })

  if (response.status === 204) {
    return null
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const message = formatErrors(data?.errors ?? data?.detail ?? data ?? {}) || 'Request failed.'
    throw new Error(message)
  }

  return data
}

function App() {
  const [mode, setMode] = useState('login')
  const [user, setUser] = useState(null)
  const [feedback, setFeedback] = useState({ type: '', message: '' })
  const [loginForm, setLoginForm] = useState({ username: '', password: '' })
  const [registerForm, setRegisterForm] = useState({
    username: '',
    email: '',
    nickname: '',
    password: '',
    password_confirm: '',
  })
  const [profileForm, setProfileForm] = useState({ nickname: '', avatar_key: 'knight-1' })

  const loadProfile = async () => {
    try {
      const profile = await apiRequest('/api/auth/me/')
      setUser(profile)
    } catch {
      setUser(null)
    }
  }

  useEffect(() => {
    loadProfile()
  }, [])

  useEffect(() => {
    if (user) {
      setProfileForm({
        nickname: user.profile.nickname,
        avatar_key: user.profile.avatar_key,
      })
    }
  }, [user])

  const handleRegister = async (event) => {
    event.preventDefault()
    setFeedback({ type: '', message: '' })

    try {
      await apiRequest('/api/auth/register/', {
        method: 'POST',
        body: JSON.stringify(registerForm),
      })
      setFeedback({ type: 'success', message: 'Registration successful. You can log in now.' })
      setMode('login')
      setRegisterForm({
        username: '',
        email: '',
        nickname: '',
        password: '',
        password_confirm: '',
      })
    } catch (error) {
      setFeedback({ type: 'error', message: error.message })
    }
  }

  const handleLogin = async (event) => {
    event.preventDefault()
    setFeedback({ type: '', message: '' })

    try {
      const profile = await apiRequest('/api/auth/login/', {
        method: 'POST',
        body: JSON.stringify(loginForm),
      })
      setUser(profile)
      setFeedback({ type: 'success', message: 'Login successful.' })
      setMode('profile')
    } catch (error) {
      setFeedback({ type: 'error', message: error.message })
    }
  }

  const handleLogout = async () => {
    try {
      await apiRequest('/api/auth/logout/', { method: 'POST' })
      setUser(null)
      setMode('login')
      setFeedback({ type: 'success', message: 'Logged out.' })
    } catch (error) {
      setFeedback({ type: 'error', message: error.message })
    }
  }

  const handleProfileUpdate = async (event) => {
    event.preventDefault()
    setFeedback({ type: '', message: '' })

    try {
      const profile = await apiRequest('/api/auth/me/', {
        method: 'PATCH',
        body: JSON.stringify(profileForm),
      })
      setUser(profile)
      setFeedback({ type: 'success', message: 'Profile updated.' })
    } catch (error) {
      setFeedback({ type: 'error', message: error.message })
    }
  }

  return (
    <main className="page-shell">
      <section className="panel">
        <div className="panel-header">
          <span className="eyebrow">Quiz Conquest</span>
          <h1>Authentication</h1>
        </div>

        {feedback.message ? (
          <div className={`feedback ${feedback.type}`}>{feedback.message}</div>
        ) : null}

        {!user ? (
          <div className="auth-shell">
            <div className="toggle-row">
              <button
                type="button"
                className={mode === 'login' ? 'toggle active' : 'toggle'}
                onClick={() => setMode('login')}
              >
                Login
              </button>
              <button
                type="button"
                className={mode === 'register' ? 'toggle active' : 'toggle'}
                onClick={() => setMode('register')}
              >
                Register
              </button>
            </div>

            {mode === 'login' ? (
              <form className="auth-form" onSubmit={handleLogin}>
                <label>
                  Username
                  <input
                    value={loginForm.username}
                    onChange={(event) => setLoginForm({ ...loginForm, username: event.target.value })}
                    placeholder="player_one"
                  />
                </label>
                <label>
                  Password
                  <input
                    type="password"
                    value={loginForm.password}
                    onChange={(event) => setLoginForm({ ...loginForm, password: event.target.value })}
                    placeholder="********"
                  />
                </label>
                <button type="submit" className="primary-button">Login</button>
              </form>
            ) : (
              <form className="auth-form" onSubmit={handleRegister}>
                <label>
                  Username
                  <input
                    value={registerForm.username}
                    onChange={(event) => setRegisterForm({ ...registerForm, username: event.target.value })}
                    placeholder="player_one"
                  />
                </label>
                <label>
                  Email
                  <input
                    type="email"
                    value={registerForm.email}
                    onChange={(event) => setRegisterForm({ ...registerForm, email: event.target.value })}
                    placeholder="player@example.com"
                  />
                </label>
                <label>
                  Nickname
                  <input
                    value={registerForm.nickname}
                    onChange={(event) => setRegisterForm({ ...registerForm, nickname: event.target.value })}
                    placeholder="MountainKnight"
                  />
                </label>
                <label>
                  Password
                  <input
                    type="password"
                    value={registerForm.password}
                    onChange={(event) => setRegisterForm({ ...registerForm, password: event.target.value })}
                    placeholder="********"
                  />
                </label>
                <label>
                  Confirm password
                  <input
                    type="password"
                    value={registerForm.password_confirm}
                    onChange={(event) => setRegisterForm({ ...registerForm, password_confirm: event.target.value })}
                    placeholder="********"
                  />
                </label>
                <button type="submit" className="primary-button">Register</button>
              </form>
            )}
          </div>
        ) : (
          <div className="profile-shell">
            <div className="profile-summary">
              <p className="label">Logged in as</p>
              <h2>{user.username}</h2>
              <p>{user.email}</p>
            </div>

            <form className="auth-form" onSubmit={handleProfileUpdate}>
              <label>
                Nickname
                <input
                  value={profileForm.nickname}
                  onChange={(event) => setProfileForm({ ...profileForm, nickname: event.target.value })}
                />
              </label>

              <label>
                Avatar
                <select
                  value={profileForm.avatar_key}
                  onChange={(event) => setProfileForm({ ...profileForm, avatar_key: event.target.value })}
                >
                  {avatarOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>

              <div className="button-row">
                <button type="submit" className="primary-button">Save profile</button>
                <button type="button" className="secondary-button" onClick={handleLogout}>Logout</button>
              </div>
            </form>
          </div>
        )}
      </section>
    </main>
  )
}

export default App
