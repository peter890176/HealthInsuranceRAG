import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import MainLayout from './layouts/MainLayout';
import SearchPage from './pages/SearchPage';
import RagQaPage from './pages/RagQaPage';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f4f6f8',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(10px)',
          color: '#333',
          boxShadow: 'inset 0 -1px 0 0 #e7eaf3'
        },
      },
    },
  },
});

function App() {
  // Shared state for both pages
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState('');
  const [searchTopK, setSearchTopK] = useState(10);
  const [searchCompletedSteps, setSearchCompletedSteps] = useState([]);
  const [searchCurrentStep, setSearchCurrentStep] = useState('');
  const [searchTranslationInfo, setSearchTranslationInfo] = useState(null);

  const [ragQuestion, setRagQuestion] = useState('');
  const [ragAnswer, setRagAnswer] = useState(null);
  const [ragLoading, setRagLoading] = useState(false);
  const [ragError, setRagError] = useState('');
  const [ragCompletedSteps, setRagCompletedSteps] = useState([]);
  const [ragCurrentStep, setRagCurrentStep] = useState('');
  const [ragTranslationInfo, setRagTranslationInfo] = useState(null);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <MainLayout>
          <Routes>
            <Route path="/" element={<Navigate replace to="/search" />} />
            <Route 
              path="/search" 
              element={
                <SearchPage 
                  query={searchQuery}
                  setQuery={setSearchQuery}
                  results={searchResults}
                  setResults={setSearchResults}
                  loading={searchLoading}
                  setLoading={setSearchLoading}
                  error={searchError}
                  setError={setSearchError}
                  topK={searchTopK}
                  setTopK={setSearchTopK}
                  completedSteps={searchCompletedSteps}
                  setCompletedSteps={setSearchCompletedSteps}
                  currentStep={searchCurrentStep}
                  setCurrentStep={setSearchCurrentStep}
                  translationInfo={searchTranslationInfo}
                  setTranslationInfo={setSearchTranslationInfo}
                />
              } 
            />
            <Route 
              path="/rag" 
              element={
                <RagQaPage 
                  question={ragQuestion}
                  setQuestion={setRagQuestion}
                  answer={ragAnswer}
                  setAnswer={setRagAnswer}
                  loading={ragLoading}
                  setLoading={setRagLoading}
                  error={ragError}
                  setError={setRagError}
                  completedSteps={ragCompletedSteps}
                  setCompletedSteps={setRagCompletedSteps}
                  currentStep={ragCurrentStep}
                  setCurrentStep={setRagCurrentStep}
                  translationInfo={ragTranslationInfo}
                  setTranslationInfo={setRagTranslationInfo}
                />
              } 
            />
          </Routes>
        </MainLayout>
      </Router>
    </ThemeProvider>
  );
}

export default App; 