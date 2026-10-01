import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from 'react-router-dom'

import HomePage from './pages/HomePage'
import AnalyzePage from './pages/AnalyzePage'
import ProcessingPage from './pages/ProcessingPage'
import ReportPage from './pages/ReportPage'


export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<HomePage />}
        />

        <Route
          path="/analyze"
          element={<AnalyzePage />}
        />

        <Route
          path="/processing"
          element={<ProcessingPage />}
        />

        <Route
          path="/report"
          element={<ReportPage />}
        />

        <Route
          path="*"
          element={
            <Navigate
              to="/"
              replace
            />
          }
        />
      </Routes>
    </BrowserRouter>
  )
}
