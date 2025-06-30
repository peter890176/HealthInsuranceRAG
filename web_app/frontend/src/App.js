import React, { useState } from 'react';
import axios from 'axios';
import { Container, Typography, TextField, Button, Box, CircularProgress, List, ListItem, ListItemText, Paper, Chip, Tabs, Tab, LinearProgress, Alert, Card, CardContent } from '@mui/material';
import { CheckCircle, RadioButtonUnchecked, RadioButtonChecked } from '@mui/icons-material';

function App() {
  const [activeTab, setActiveTab] = useState(0);
  const [query, setQuery] = useState('');
  const [question, setQuestion] = useState('');
  const [results, setResults] = useState([]);
  const [ragAnswer, setRagAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [topK, setTopK] = useState(10);
  const [translationInfo, setTranslationInfo] = useState(null);
  const [currentStep, setCurrentStep] = useState('');
  const [progress, setProgress] = useState(0);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [translationStepInfo, setTranslationStepInfo] = useState(null);

  // Define step configurations
  const searchSteps = [
    { id: 'detect', label: 'Detecting non-English characters in query...', progress: 10 },
    { id: 'translate', label: 'Translating query to English...', progress: 20 },
    { id: 'embed', label: 'Generating query embedding...', progress: 40 },
    { id: 'search', label: 'Searching in vector database...', progress: 60 },
    { id: 'retrieve', label: 'Retrieving article details...', progress: 80 },
    { id: 'complete', label: 'Search completed!', progress: 100 }
  ];

  const ragSteps = [
    { id: 'detect', label: 'Detecting non-English characters in question...', progress: 10 },
    { id: 'translate', label: 'Translating question to English...', progress: 20 },
    { id: 'embed', label: 'Generating question embedding...', progress: 30 },
    { id: 'search', label: 'Searching for relevant articles...', progress: 50 },
    { id: 'retrieve', label: 'Retrieving article details...', progress: 70 },
    { id: 'context', label: 'Building context from articles...', progress: 80 },
    { id: 'generate', label: 'Generating AI answer...', progress: 90 },
    { id: 'complete', label: 'RAG analysis completed!', progress: 100 }
  ];

  const getCurrentSteps = () => {
    return activeTab === 0 ? searchSteps : ragSteps;
  };

  const getStepStatus = (step) => {
    // Check if this step is completed
    if (completedSteps.includes(step.label)) {
      return 'completed';
    } 
    // Check if this step is currently being processed
    else if (currentStep === step.label) {
      return 'current';
    } 
    // Check if any step after this one is completed (meaning this step should be completed)
    else {
      const currentStepIndex = getCurrentSteps().findIndex(s => s.label === step.label);
      const completedStepIndex = getCurrentSteps().findIndex(s => completedSteps.includes(s.label));
      
      if (completedStepIndex > currentStepIndex) {
        return 'completed';
      } else {
        return 'pending';
      }
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    setError('');
    setResults([]);
    setTranslationInfo(null);
    setTranslationStepInfo(null);
    setCurrentStep('');
    setProgress(0);
    setCompletedSteps([]);
    
    try {
      const response = await fetch('http://localhost:5000/api/search_with_progress', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          top_k: topK
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.error) {
                setError(data.error);
                setLoading(false);
                return;
              }
              
              if (data.step) {
                setCurrentStep(data.step);
                setProgress(data.progress);
                setCompletedSteps(prev => [...prev, data.step]);
                
                // Handle translation step information
                if (data.translation_info) {
                  setTranslationStepInfo({
                    original: data.translation_info.replace('Original: ', ''),
                    step: data.step
                  });
                }
                if (data.translation_result) {
                  setTranslationStepInfo(prev => ({
                    ...prev,
                    translated: data.translation_result.replace('Translated: ', ''),
                    step: data.step
                  }));
                }
              }
              
              if (data.complete) {
                setResults(data.results);
                
                // Show translation info if translation was performed
                if (data.original_query !== data.translated_query) {
                  setTranslationInfo({
                    original: data.original_query,
                    translated: data.translated_query
                  });
                }
                
                setLoading(false);
                return;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (err) {
      setError(err.message || 'Search failed');
      setLoading(false);
    }
  };

  const handleRagQuestion = async () => {
    setLoading(true);
    setError('');
    setRagAnswer(null);
    setTranslationStepInfo(null);
    setCurrentStep('');
    setProgress(0);
    setCompletedSteps([]);
    
    try {
      const response = await fetch('http://localhost:5000/api/rag_qa_with_progress', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          top_k: 8
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.error) {
                setError(data.error);
                setLoading(false);
                return;
              }
              
              if (data.step) {
                setCurrentStep(data.step);
                setProgress(data.progress);
                setCompletedSteps(prev => [...prev, data.step]);
                
                // Handle translation step information
                if (data.translation_info) {
                  setTranslationStepInfo({
                    original: data.translation_info.replace('Original: ', ''),
                    step: data.step
                  });
                }
                if (data.translation_result) {
                  setTranslationStepInfo(prev => ({
                    ...prev,
                    translated: data.translation_result.replace('Translated: ', ''),
                    step: data.step
                  }));
                }
              }
              
              if (data.complete) {
                setRagAnswer(data);
                setLoading(false);
                return;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (err) {
      setError(err.message || 'RAG QA failed');
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    setResults([]);
    setRagAnswer(null);
    setError('');
    setCurrentStep('');
    setProgress(0);
    setCompletedSteps([]);
    setTranslationStepInfo(null);
  };

  const TimelineStep = ({ step, status, isLast }) => {
    const getStepIcon = () => {
      switch (status) {
        case 'completed':
          return <CheckCircle sx={{ color: 'success.main', fontSize: 24 }} />;
        case 'current':
          return <RadioButtonChecked sx={{ color: 'primary.main', fontSize: 24 }} />;
        default:
          return <RadioButtonUnchecked sx={{ color: 'grey.400', fontSize: 24 }} />;
      }
    };

    const getStepColor = () => {
      switch (status) {
        case 'completed':
          return 'success.main';
        case 'current':
          return 'primary.main';
        default:
          return 'grey.400';
      }
    };

    // Get display name (remove trailing dots and ellipsis)
    const getDisplayName = (label) => {
      return label.replace(/\.\.\.$/, '').replace(/!$/, '');
    };

    // Check if this step has translation info
    const hasTranslationInfo = translationStepInfo && 
      (step.label.includes('Translating') || step.label.includes('Translation completed') || step.label.includes('skipping translation'));

    return (
      <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            width: 40,
            height: 40,
            borderRadius: '50%',
            bgcolor: status === 'current' ? 'primary.50' : 'background.paper',
            border: 2,
            borderColor: getStepColor(),
            mb: 1
          }}>
            {getStepIcon()}
          </Box>
          <Typography 
            variant="caption" 
            sx={{ 
              textAlign: 'center',
              color: getStepColor(),
              fontWeight: status === 'current' ? 'bold' : 'normal',
              fontSize: '0.7rem',
              maxWidth: 120,
              lineHeight: 1.2
            }}
          >
            {getDisplayName(step.label)}
          </Typography>
          
          {/* Show translation info if this step has it */}
          {hasTranslationInfo && translationStepInfo && (
            <Box sx={{ 
              mt: 1, 
              p: 1, 
              bgcolor: 'info.50', 
              borderRadius: 1, 
              border: '1px solid',
              borderColor: 'info.200',
              maxWidth: 150,
              fontSize: '0.6rem'
            }}>
              {translationStepInfo.original && (
                <Typography variant="caption" display="block" color="text.secondary">
                  <strong>Original:</strong> {translationStepInfo.original.length > 20 ? 
                    translationStepInfo.original.substring(0, 20) + '...' : 
                    translationStepInfo.original}
                </Typography>
              )}
              {translationStepInfo.translated && (
                <Typography variant="caption" display="block" color="primary.main">
                  <strong>Translated:</strong> {translationStepInfo.translated.length > 20 ? 
                    translationStepInfo.translated.substring(0, 20) + '...' : 
                    translationStepInfo.translated}
                </Typography>
              )}
            </Box>
          )}
        </Box>
        {!isLast && (
          <Box sx={{ 
            flex: 1,
            height: 2, 
            bgcolor: status === 'completed' ? 'success.main' : 'grey.300',
            mx: 1,
            transition: 'background-color 0.3s ease'
          }} />
        )}
      </Box>
    );
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom align="center">
        PubMed Semantic Search & RAG QA
      </Typography>
      <Typography variant="subtitle1" align="center" color="text.secondary" sx={{ mb: 3 }}>
        Support Chinese-English mixed queries with AI translation and question answering
      </Typography>
      
      <Tabs value={activeTab} onChange={handleTabChange} centered sx={{ mb: 3 }}>
        <Tab label="Semantic Search" />
        <Tab label="RAG Question Answering" />
      </Tabs>

      {activeTab === 0 && (
        <Box>
          <Box display="flex" gap={2} mb={2}>
            <TextField
              label="Enter your query (支持中英文混合)"
              variant="outlined"
              fullWidth
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') handleSearch(); }}
              placeholder="e.g., 糖尿病 diabetes treatment, heart disease 預防"
            />
            <TextField
              label="Top K"
              type="number"
              variant="outlined"
              value={topK}
              onChange={e => setTopK(Number(e.target.value))}
              sx={{ width: 100 }}
            />
            <Button variant="contained" color="primary" onClick={handleSearch} disabled={loading}>
              Search
            </Button>
          </Box>
          
          {/* Timeline Flow Chart - Moved here */}
          {(loading || completedSteps.length > 0) && (
            <Box sx={{ mb: 3 }}>
              <Paper sx={{ p: 3, bgcolor: 'grey.50' }}>
                <Typography variant="h6" gutterBottom align="center">
                  {loading ? 'Processing Timeline' : 'Processing Completed'}
                </Typography>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  overflowX: 'auto',
                  py: 2,
                  px: 1
                }}>
                  {getCurrentSteps().map((step, index) => (
                    <TimelineStep 
                      key={step.id}
                      step={step} 
                      status={getStepStatus(step)}
                      isLast={index === getCurrentSteps().length - 1}
                    />
                  ))}
                </Box>
                {currentStep && loading && (
                  <Typography variant="body2" align="center" color="primary.main" sx={{ mt: 2 }}>
                    Current: {currentStep}
                  </Typography>
                )}
                {!loading && completedSteps.length > 0 && (
                  <Typography variant="body2" align="center" color="success.main" sx={{ mt: 2 }}>
                    ✅ All steps completed successfully!
                  </Typography>
                )}
                
                {/* Show detailed translation info after completion */}
                {!loading && translationStepInfo && translationStepInfo.translated && (
                  <Box sx={{ mt: 2, p: 2, bgcolor: 'info.50', borderRadius: 1, border: '1px solid', borderColor: 'info.200' }}>
                    <Typography variant="subtitle2" gutterBottom color="info.main">
                      Translation Details
                    </Typography>
                    <Box display="flex" flexDirection="column" gap={1}>
                      <Typography variant="body2">
                        <strong>Original:</strong> {translationStepInfo.original}
                      </Typography>
                      <Typography variant="body2" color="primary.main">
                        <strong>Translated:</strong> {translationStepInfo.translated}
                      </Typography>
                    </Box>
                  </Box>
                )}
              </Paper>
            </Box>
          )}
          
          {results.length > 0 && (
            <Typography variant="h6" gutterBottom>
              Search Results ({results.length} articles)
            </Typography>
          )}
          
          <List>
            {results.map((item, idx) => (
              <Paper key={item.pmid} sx={{ mb: 2, p: 2 }} elevation={2}>
                <Typography variant="h6" gutterBottom>{item.title}</Typography>
                <Box display="flex" gap={1} mb={1} flexWrap="wrap">
                  <Chip label={`PMID: ${item.pmid}`} size="small" variant="outlined" />
                  <Chip label={item.journal} size="small" variant="outlined" />
                  <Chip label={item.pub_date} size="small" variant="outlined" />
                  <Chip 
                    label={`Similarity: ${(item.similarity_score * 100).toFixed(1)}%`} 
                    size="small" 
                    color="primary" 
                  />
                </Box>
                <Typography variant="body2" sx={{ mt: 1, mb: 1 }}>
                  {item.abstract}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Authors: {item.authors.join(', ')}
                </Typography>
              </Paper>
            ))}
          </List>
        </Box>
      )}

      {activeTab === 1 && (
        <Box>
          <Box display="flex" gap={2} mb={2}>
            <TextField
              label="Ask a medical question (支持中英文混合)"
              variant="outlined"
              fullWidth
              multiline
              rows={3}
              value={question}
              onChange={e => setQuestion(e.target.value)}
              placeholder="e.g., What are the latest treatments for diabetes? 台灣健保改革的歷史如何？"
            />
            <Button variant="contained" color="primary" onClick={handleRagQuestion} disabled={loading}>
              Ask
            </Button>
          </Box>
          
          {/* Timeline Flow Chart - Moved here for RAG */}
          {(loading || completedSteps.length > 0) && (
            <Box sx={{ mb: 3 }}>
              <Paper sx={{ p: 3, bgcolor: 'grey.50' }}>
                <Typography variant="h6" gutterBottom align="center">
                  {loading ? 'Processing Timeline' : 'Processing Completed'}
                </Typography>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  overflowX: 'auto',
                  py: 2,
                  px: 1
                }}>
                  {getCurrentSteps().map((step, index) => (
                    <TimelineStep 
                      key={step.id}
                      step={step} 
                      status={getStepStatus(step)}
                      isLast={index === getCurrentSteps().length - 1}
                    />
                  ))}
                </Box>
                {currentStep && loading && (
                  <Typography variant="body2" align="center" color="primary.main" sx={{ mt: 2 }}>
                    Current: {currentStep}
                  </Typography>
                )}
                {!loading && completedSteps.length > 0 && (
                  <Typography variant="body2" align="center" color="success.main" sx={{ mt: 2 }}>
                    ✅ All steps completed successfully!
                  </Typography>
                )}
                
                {/* Show detailed translation info after completion */}
                {!loading && translationStepInfo && translationStepInfo.translated && (
                  <Box sx={{ mt: 2, p: 2, bgcolor: 'info.50', borderRadius: 1, border: '1px solid', borderColor: 'info.200' }}>
                    <Typography variant="subtitle2" gutterBottom color="info.main">
                      Translation Details
                    </Typography>
                    <Box display="flex" flexDirection="column" gap={1}>
                      <Typography variant="body2">
                        <strong>Original:</strong> {translationStepInfo.original}
                      </Typography>
                      <Typography variant="body2" color="primary.main">
                        <strong>Translated:</strong> {translationStepInfo.translated}
                      </Typography>
                    </Box>
                  </Box>
                )}
              </Paper>
            </Box>
          )}
          
          {ragAnswer && (
            <Box>
              <Paper sx={{ p: 3, mb: 3, bgcolor: 'success.light' }}>
                <Typography variant="h6" gutterBottom>
                  AI Answer
                </Typography>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {ragAnswer.answer}
                </Typography>
                <Box mt={2}>
                  <Typography variant="caption" color="text.secondary">
                    Based on {ragAnswer.articles_used} relevant articles
                  </Typography>
                </Box>
              </Paper>
              
              <Typography variant="h6" gutterBottom>
                Supporting Articles ({ragAnswer.relevant_articles.length})
              </Typography>
              
              <List>
                {ragAnswer.relevant_articles.map((item, idx) => (
                  <Paper key={item.pmid} sx={{ mb: 2, p: 2 }} elevation={1}>
                    <Typography variant="h6" gutterBottom>{item.title}</Typography>
                    <Box display="flex" gap={1} mb={1} flexWrap="wrap">
                      <Chip label={`PMID: ${item.pmid}`} size="small" variant="outlined" />
                      <Chip label={item.journal} size="small" variant="outlined" />
                      <Chip label={item.pub_date} size="small" variant="outlined" />
                      <Chip 
                        label={`Relevance: ${(item.similarity_score * 100).toFixed(1)}%`} 
                        size="small" 
                        color="secondary" 
                      />
                    </Box>
                    <Typography variant="body2" sx={{ mt: 1, mb: 1 }}>
                      {item.abstract}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Authors: {item.authors.join(', ')}
                    </Typography>
                  </Paper>
                ))}
              </List>
            </Box>
          )}
        </Box>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Container>
  );
}

export default App;
