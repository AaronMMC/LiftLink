import { useState } from "react";
import { searchInstructors } from "../../services/api";

export default function SearchInstructors() {
  const [specialty, setSpecialty] = useState("");
  const [location, setLocation] = useState("");
  const [results, setResults] = useState([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!specialty) return setError("Please select a specialty");
    setError("");
    setLoading(true);
    try {
      const params = { specialty };
      if (location) params.location = location;
      const res = await searchInstructors(params);
      setResults(res.data.instructors);
      setSearched(true);
    } catch (err) {
      setError("Search failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-page">
      <h1>Find Instructors</h1>
      <p className="subtitle">Discover the perfect trainer for your goals</p>

      <form onSubmit={handleSearch} className="search-form glass">
        <div className="search-fields">
          <select value={specialty} onChange={(e) => setSpecialty(e.target.value)} className="search-input">
            <option value="">Select Specialty...</option>
            <option value="yoga">Yoga</option>
            <option value="pilates">Pilates</option>
            <option value="strength">Strength Training</option>
            <option value="cardio">Cardio</option>
            <option value="crossfit">CrossFit</option>
            <option value="nutrition">Nutrition</option>
          </select>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Location (optional)"
            className="search-input"
          />
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      </form>

      {error && <div className="alert alert-error">{error}</div>}

      {searched && (
        <div className="results-section">
          <h2>{results.length} instructor{results.length !== 1 ? "s" : ""} found</h2>
          <div className="instructor-grid">
            {results.map((inst) => (
              <div key={inst.instructor_id} className="instructor-card glass">
                <div className="instructor-avatar">
                  {inst.display_name.charAt(0).toUpperCase()}
                </div>
                <h3>{inst.display_name}</h3>
                <div className="instructor-meta">
                  <span className="badge">{inst.specialty}</span>
                  <span className="location">📍 {inst.location}</span>
                </div>
                {inst.bio && <p className="instructor-bio">{inst.bio}</p>}
              </div>
            ))}
            {results.length === 0 && (
              <p className="no-results">No instructors found. Try a different search.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
