import React from 'react';
import { Navigate } from 'react-router-dom';

export const AchievementsPage: React.FC = () => {
  return <Navigate to="/student/dashboard" replace />;
};
