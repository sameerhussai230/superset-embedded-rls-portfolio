// src/App.jsx
import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import LoginPage from './components/LoginPage';
import DashboardPage from './components/DashboardPage';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

function App() {
  // State remains the same
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('isLoggedIn'));
  const [userType, setUserType] = useState(localStorage.getItem('userType') || null); // 'admin', 'manufacturer', or null
  const [userIdentifier, setUserIdentifier] = useState(localStorage.getItem('userIdentifier') || null); // 'admin' or Manufacturer Name
  const navigate = useNavigate();
  const location = useLocation();

  // handleLoginSuccess remains the same
  const handleLoginSuccess = (type, identifier) => {
    localStorage.setItem('isLoggedIn', 'true');
    localStorage.setItem('userType', type);
    localStorage.setItem('userIdentifier', identifier);
    setIsAuthenticated(true);
    setUserType(type);
    setUserIdentifier(identifier);

    if (type === 'admin') {
      navigate('/dashboard/full');
    } else if (type === 'manufacturer') {
      navigate(`/dashboard/rls/${encodeURIComponent(identifier)}`);
    } else {
      navigate('/login');
    }
  };

  // handleLogout remains the same
  const handleLogout = () => {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userType');
    localStorage.removeItem('userIdentifier');
    setIsAuthenticated(false);
    setUserType(null);
    setUserIdentifier(null);
    navigate('/login');
  };

  // useEffect for state synchronization remains the same
  useEffect(() => {
    const checkAuth = () => {
      const loggedIn = !!localStorage.getItem('isLoggedIn');
      const storedType = localStorage.getItem('userType');
      const storedIdentifier = localStorage.getItem('userIdentifier');

      if (isAuthenticated !== loggedIn) setIsAuthenticated(loggedIn);
      if (userType !== storedType) setUserType(storedType);
      if (userIdentifier !== storedIdentifier) setUserIdentifier(storedIdentifier);

      if (!loggedIn && isAuthenticated) {
          setIsAuthenticated(false);
          setUserType(null);
          setUserIdentifier(null);
      }
    };
    checkAuth();
    window.addEventListener('storage', checkAuth);
    return () => window.removeEventListener('storage', checkAuth);
  }, [isAuthenticated, userType, userIdentifier]);


  // getDefaultAuthenticatedPath remains the same
  const getDefaultAuthenticatedPath = () => {
      if (userType === 'admin') {
          return '/dashboard/full';
      } else if (userType === 'manufacturer' && userIdentifier) {
          return `/dashboard/rls/${encodeURIComponent(userIdentifier)}`;
      }
      return '/login';
  };

  return (
    <div className="app-container">
      {/* Header rendering condition remains the same */}
      {isAuthenticated && userIdentifier && (
        <header className="app-header">
          <h1>Superset Embedded Dashboard</h1>
          <nav>
            {/* --- MODIFICATION START: Conditional Button Rendering --- */}
            {/* Show RLS button only for manufacturers */}
            {userType === 'manufacturer' && (
              <button onClick={() => navigate(`/dashboard/rls/${encodeURIComponent(userIdentifier)}`)}>
                View My Dashboard (RLS)
              </button>
            )}
            {/* Show Full Dashboard button ONLY for admin */}
            {userType === 'admin' && (
              <button onClick={() => navigate('/dashboard/full')}>
                View Full Dashboard
              </button>
            )}
            {/* --- MODIFICATION END --- */}

            {/* Logout button remains the same */}
            <button onClick={handleLogout} className="logout-button">
              Logout ({userIdentifier})
            </button>
          </nav>
        </header>
      )}
      <main className="content-area">
        <Routes>
          {/* Login route remains the same */}
          <Route
            path="/login"
            element={
              isAuthenticated ? (
                <Navigate to={getDefaultAuthenticatedPath()} replace />
              ) : (
                <LoginPage onLoginSuccess={handleLoginSuccess} />
              )
            }
          />
          {/* RLS route remains the same, protected for manufacturers */}
          <Route
            path="/dashboard/rls/:manufacturer"
            element={
              <ProtectedRoute isAuthenticated={isAuthenticated} allowedUserType="manufacturer">
                <ErrorBoundary>
                  <DashboardPage mode="rls" />
                </ErrorBoundary>
              </ProtectedRoute>
            }
          />
          {/* --- MODIFICATION START: Protect Full Dashboard Route --- */}
          {/* Full route now explicitly requires 'admin' user type */}
          <Route
            path="/dashboard/full"
            element={
              <ProtectedRoute isAuthenticated={isAuthenticated} allowedUserType="admin">
                <ErrorBoundary>
                  <DashboardPage mode="full" />
                </ErrorBoundary>
              </ProtectedRoute>
            }
          />
          {/* --- MODIFICATION END --- */}

          {/* Default route remains the same */}
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <Navigate to={getDefaultAuthenticatedPath()} replace />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          {/* Catch-all route remains the same */}
          <Route path="*" element={<Navigate to={isAuthenticated ? getDefaultAuthenticatedPath() : "/login"} replace />} />
        </Routes>
      </main>
    </div>
  );
}

// ProtectedRoute component remains the same - its logic already handles the allowedUserType check
function ProtectedRoute({ isAuthenticated, children, allowedUserType = null }) {
  const location = useLocation();
  const userType = localStorage.getItem('userType'); // Get type from storage for check

  if (!isAuthenticated) {
    // Not logged in, redirect to login
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If a specific user type is required, check it
  if (allowedUserType && userType !== allowedUserType) {
      // Logged in, but wrong user type for this route
      console.warn(`Access denied: Route requires user type '${allowedUserType}', but user is '${userType}'. Redirecting.`);
      // Determine the correct default path based on the *actual* user type
      const actualUserDefaultPath = userType === 'admin'
          ? '/dashboard/full'
          : userType === 'manufacturer' && localStorage.getItem('userIdentifier')
          ? `/dashboard/rls/${encodeURIComponent(localStorage.getItem('userIdentifier'))}`
          : '/login'; // Fallback if identifier is missing or type is unknown
      return <Navigate to={actualUserDefaultPath} replace />;
  }

  // Authenticated and (if required) correct user type
  return children;
}

export default App;