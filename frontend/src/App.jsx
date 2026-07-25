import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import InstructorDashboard from "./pages/instructor/InstructorDashboard";
import CreateProfile from "./pages/instructor/CreateProfile";
import EditProfile from "./pages/instructor/EditProfile";
import LogProgress from "./pages/instructor/LogProgress";
import ClientDashboard from "./pages/client/ClientDashboard";
import SearchInstructors from "./pages/client/SearchInstructors";
import ProgressHistory from "./pages/client/ProgressHistory";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />

        {/* Instructor routes */}
        <Route path="/instructor/dashboard" element={
          <ProtectedRoute requiredRole="instructor"><InstructorDashboard /></ProtectedRoute>
        } />
        <Route path="/instructor/profile/create" element={
          <ProtectedRoute requiredRole="instructor"><CreateProfile /></ProtectedRoute>
        } />
        <Route path="/instructor/profile/edit" element={
          <ProtectedRoute requiredRole="instructor"><EditProfile /></ProtectedRoute>
        } />
        <Route path="/instructor/progress" element={
          <ProtectedRoute requiredRole="instructor"><LogProgress /></ProtectedRoute>
        } />

        {/* Client routes */}
        <Route path="/client/dashboard" element={
          <ProtectedRoute requiredRole="client"><ClientDashboard /></ProtectedRoute>
        } />
        <Route path="/client/search" element={
          <ProtectedRoute requiredRole="client"><SearchInstructors /></ProtectedRoute>
        } />
        <Route path="/client/history" element={
          <ProtectedRoute requiredRole="client"><ProgressHistory /></ProtectedRoute>
        } />
      </Routes>
    </Layout>
  );
}
