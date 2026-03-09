import { Navigate, Route, Routes } from "react-router-dom";

import AppLayout from "./components/layout/AppLayout";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./routes/ProtectedRoute";

import CareerPlanner from "./pages/CareerPlanner";
import Dashboard from "./pages/Dashboard";
import DynamicQuiz from "./pages/DynamicQuiz";
import InterviewSimulator from "./pages/InterviewSimulator";
import LearningResources from "./pages/LearningResources";
import Login from "./pages/Login";
import MarketInsights from "./pages/MarketInsights";
import NotFound from "./pages/NotFound";
import Register from "./pages/Register";
import ResumeUpload from "./pages/ResumeUploadFormatted";
import SkillsEvaluation from "./pages/SkillsEvaluation";

function ProtectedPage({ children }) {
  return (
    <ProtectedRoute>
      <AppLayout>{children}</AppLayout>
    </ProtectedRoute>
  );
}

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/"
          element={
            <ProtectedPage>
              <Dashboard />
            </ProtectedPage>
          }
        />
        <Route
          path="/career-support"
          element={
            <ProtectedPage>
              <CareerPlanner />
            </ProtectedPage>
          }
        />
        <Route
          path="/resume-analysis"
          element={
            <ProtectedPage>
              <ResumeUpload />
            </ProtectedPage>
          }
        />
        <Route
          path="/skills-evaluation"
          element={
            <ProtectedPage>
              <SkillsEvaluation />
            </ProtectedPage>
          }
        />
        <Route
          path="/dynamic-quiz"
          element={
            <ProtectedPage>
              <DynamicQuiz />
            </ProtectedPage>
          }
        />
        <Route
          path="/learning-resources"
          element={
            <ProtectedPage>
              <LearningResources />
            </ProtectedPage>
          }
        />
        <Route
          path="/interview-simulator"
          element={
            <ProtectedPage>
              <InterviewSimulator />
            </ProtectedPage>
          }
        />
        <Route
          path="/market-insights"
          element={
            <ProtectedPage>
              <MarketInsights />
            </ProtectedPage>
          }
        />

        <Route path="*" element={<NotFound />} />
        <Route path="" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
