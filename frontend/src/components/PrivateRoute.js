import React from 'react';
import { Navigate } from 'react-router-dom';

function PrivateRoute({ children }) {
  // TODO: Replace with actual authentication check
  const isAuthenticated = false;

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return children;
}

export default PrivateRoute; 