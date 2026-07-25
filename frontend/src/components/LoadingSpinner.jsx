export default function LoadingSpinner({ message = "Loading..." }) {
  return (
    <div className="loading-container">
      <div className="spinner" />
      <p style={{ marginTop: "1rem", color: "var(--text-secondary)" }}>{message}</p>
    </div>
  );
}
