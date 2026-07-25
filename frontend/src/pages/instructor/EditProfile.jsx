import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { getProfile, updateProfile } from "../../services/api";
import LoadingSpinner from "../../components/LoadingSpinner";

export default function EditProfile() {
  const { user } = useAuth();
  const [form, setForm] = useState({ display_name: "", specialty: "", location: "", bio: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    getProfile(user.id)
      .then((res) => setForm(res.data))
      .catch(() => setError("Failed to load profile"))
      .finally(() => setLoading(false));
  }, [user.id]);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      await updateProfile(user.id, form);
      navigate("/instructor/dashboard");
    } catch (err) {
      setError(err.response?.data?.error || "Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading profile..." />;

  return (
    <div className="form-page">
      <div className="form-card glass">
        <h2>Edit Profile</h2>
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
              <input id="location" name="location" value={form.location} onChange={handleChange} required />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="bio">Bio</label>
            <textarea id="bio" name="bio" value={form.bio} onChange={handleChange} rows={4} />
          </div>
          <button type="submit" className="btn btn-primary btn-full" disabled={saving}>
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </form>
      </div>
    </div>
  );
}
