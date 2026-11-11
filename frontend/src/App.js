import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

/**
 * Main Application Component
 *
 * This React app provides:
 *   1. A health check button to verify the API and database are running.
 *   2. A form to add new student records.
 *   3. A table displaying all student records.
 *
 * All API calls go through /api/* which Nginx reverse-proxies
 * to the FastAPI backend container.
 */
function App() {
  // ── State ──────────────────────────────────────────────
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [healthStatus, setHealthStatus] = useState(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [form, setForm] = useState({ name: '', email: '', course: '' });
  const [submitting, setSubmitting] = useState(false);

  // ── Fetch Students ─────────────────────────────────────
  const fetchStudents = useCallback(async () => {
    try {
      const res = await fetch('/api/students');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setStudents(data);
    } catch (err) {
      console.error('Failed to fetch students:', err);
      setMessage({ type: 'error', text: `Failed to load students: ${err.message}` });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStudents();
  }, [fetchStudents]);

  // ── Health Check ───────────────────────────────────────
  const checkHealth = async () => {
    setHealthLoading(true);
    setHealthStatus(null);
    try {
      const res = await fetch('/api/health');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setHealthStatus({ ok: true, data });
    } catch (err) {
      setHealthStatus({ ok: false, error: err.message });
    } finally {
      setHealthLoading(false);
    }
  };

  // ── Add Student ────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);
    try {
      const res = await fetch('/api/students', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      setForm({ name: '', email: '', course: '' });
      setMessage({ type: 'success', text: 'Student added successfully!' });
      fetchStudents();
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setSubmitting(false);
    }
  };

  // ── Delete Student ─────────────────────────────────────
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this student?')) return;
    try {
      const res = await fetch(`/api/students/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setMessage({ type: 'success', text: 'Student deleted.' });
      fetchStudents();
    } catch (err) {
      setMessage({ type: 'error', text: `Delete failed: ${err.message}` });
    }
  };

  // ── Render ─────────────────────────────────────────────
  return (
    <div className="app">
      {/* Header */}
      <div className="header">
        <h1>🎓 Student Records</h1>
        <p>Project 16 — Docker &amp; Nginx Troubleshooting Demo</p>
      </div>

      {/* Health Check */}
      <div className="card">
        <h2>🩺 System Health Check</h2>
        <div className="health-section">
          <button className="health-btn" onClick={checkHealth} disabled={healthLoading}>
            {healthLoading ? 'Checking...' : 'Check Health'}
          </button>
          {healthStatus && (
            <span className={`health-status ${healthStatus.ok ? 'healthy' : 'error'}`}>
              {healthStatus.ok
                ? `✅ API: ${healthStatus.data.status} | DB: ${healthStatus.data.database}`
                : `❌ Error: ${healthStatus.error}`}
            </span>
          )}
        </div>
      </div>

      {/* Add Student Form */}
      <div className="card">
        <h2>➕ Add New Student</h2>
        {message && (
          <div className={`message ${message.type}`}>{message.text}</div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                id="name"
                type="text"
                placeholder="e.g. John Doe"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                placeholder="e.g. john@example.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
              />
            </div>
            <div className="form-group full-width">
              <label htmlFor="course">Course</label>
              <input
                id="course"
                type="text"
                placeholder="e.g. Computer Science"
                value={form.course}
                onChange={(e) => setForm({ ...form, course: e.target.value })}
                required
              />
            </div>
            <button type="submit" className="submit-btn" disabled={submitting}>
              {submitting ? 'Saving...' : 'Add Student'}
            </button>
          </div>
        </form>
      </div>

      {/* Student List */}
      <div className="card">
        <h2>📋 Student Records</h2>
        {loading ? (
          <div className="loading">Loading students...</div>
        ) : students.length === 0 ? (
          <div className="empty-state">
            <div className="icon">📭</div>
            <p>No students yet. Add one above!</p>
          </div>
        ) : (
          <table className="student-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Course</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s) => (
                <tr key={s.id}>
                  <td>{s.id}</td>
                  <td>{s.name}</td>
                  <td>{s.email}</td>
                  <td>{s.course}</td>
                  <td>
                    <button className="delete-btn" onClick={() => handleDelete(s.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Footer */}
      <div className="footer">
        <p>Project 16 — Troubleshooting 502 Bad Gateway | Docker &amp; Jenkins Assignment</p>
      </div>
    </div>
  );
}

export default App;
