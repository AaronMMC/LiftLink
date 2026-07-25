import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createProfile } from "../../services/api";

export default function CreateProfile() {
  const [form, setForm] = useState({ display_name: "", specialty: "", location: "", bio: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await createProfile(form);
      navigate("/instructor/dashboard");
    } catch (err) {
      setError(err.response?.data?.error || "Failed to create profile");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-page">
      <div className="form-card glass">
        <h2>Create Your Profile</h2>
        <p className="subtitle">Tell clients about yourself</p>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="display_name">Display Name</label>
            <input id="display_name" name="display_name" value={form.display_name} onChange={handleChange} required />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="specialty">Specialty</label>
              <select id="specialty" name="specialty" value={form.specialty} onChange={handleChange} required>
                <option value="">Select...</option>
                <option value="yoga">Yoga</option>
                <option value="pilates">Pilates</option>
                <option value="strength">Strength Training</option>
                <option value="cardio">Cardio</option>
                <option value="crossfit">CrossFit</option>
                <option value="nutrition">Nutrition</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="location">Location</label>
              <input id="location" name="location" value={form.location} onChange={handleChange} placeholder="e.g., New York" required />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="bio">Bio</label>
            <textarea id="bio" name="bio" value={form.bio} onChange={handleChange} rows={4} placeholder="Tell clients about your experience..." />
          </div>
          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? "Creating..." : "Create Profile"}
          </button>
        </form>
      </div>
    </div>
  );
}
