import { createContext, useContext, useState, useEffect } from "react";
import { getCurrentUser, signIn as authSignIn, signUp as authSignUp, signOut as authSignOut } from "../services/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    await authSignIn(email, password);
    const currentUser = await getCurrentUser();
    setUser(currentUser);
    return currentUser;
  };

  const register = async (email, password, role) => {
    await authSignUp(email, password, role);
  };

  const logout = () => {
    authSignOut();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
