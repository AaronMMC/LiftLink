import { useState } from "react";
import { createEntry } from "../../services/api";

export default function LogProgress() {
  const [form, setForm] = useState({ client_id: "", workout_type: "", notes: "", duration_minutes: 60 });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const value = e.target.type === "number" ? parseInt(e.target.value, 10) : e.target.value;
    setForm({ ...form, [e.target.name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      const res = await createEntry(form);
      setSuccess(`Progress entry logged! (ID: ${res.data.entry_id.slice(0, 8)}...)`);
      setForm({ client_id: "", workout_type: "", notes: "", duration_minutes: 60 });
    } catch (err) {
      setError(err.response?.data?.error || "Failed to log progress");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-page">
      <div className="form-card glass">
        <h2>Log Progress Entry</h2>
        <p className="subtitle">Record a client's workout session</p>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="client_id">Client ID</label>
            <input id="client_id" name="client_id" value={form.client_id} onChange={handleChange} placeholder="Client's user ID" required />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="workout_type">Workout Type</label>
              <select id="workout_type" name="workout_type" value={form.workout_type} onChange={handleChange} required>
                <option value="">Select...</option>
                <option value="Strength Training">Strength Training</option>
                <option value="Cardio">Cardio</option>
                <option value="Yoga">Yoga</option>
                <option value="Pilates">Pilates</option>
                <option value="CrossFit">CrossFit</option>
                <option value="Flexibility">Flexibility</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="duration_minutes">Duration (min)</label>
              <input id="duration_minutes" name="duration_minutes" type="number" value={form.duration_minutes} onChange={handleChange} min={1} max={300} />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="notes">Session Notes</label>
            <textarea id="notes" name="notes" value={form.notes} onChange={handleChange} rows={4} placeholder="Exercises, sets, reps, observations..." required />
          </div>
          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? "Logging..." : "Log Entry"}
          </button>
        </form>
      </div>
    </div>
  );
}
