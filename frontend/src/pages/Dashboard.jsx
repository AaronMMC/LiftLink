import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Dashboard() {
  const { user, loading } = useAuth();

  if (loading) return <LoadingSpinner />;
  if (!user) return <Navigate to="/login" replace />;

  if (user.role === "instructor") return <Navigate to="/instructor/dashboard" replace />;
  return <Navigate to="/client/dashboard" replace />;
}
