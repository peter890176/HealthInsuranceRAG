import React, { useState } from 'react';
import axios from 'axios';
import { Container, Typography, TextField, Button, Box, CircularProgress, List, ListItem, ListItemText, Paper, Chip, Tabs, Tab, LinearProgress, Alert } from '@mui/material';

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

  const handleSearch = async () => {
    setLoading(true);
    setError('');
    setResults([]);
    setTranslationInfo(null);
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
          
          {translationInfo && (
            <Paper sx={{ p: 2, mb: 2, bgcolor: 'info.light' }}>
              <Typography variant="h6" gutterBottom>
                Translation Information
              </Typography>
              <Box display="flex" gap={1} alignItems="center" flexWrap="wrap">
                <Typography variant="body2">
                  <strong>Original:</strong> {translationInfo.original}
                </Typography>
                <Typography variant="body2">
                  <strong>Translated:</strong> {translationInfo.translated}
                </Typography>
              </Box>
            </Paper>
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
      
      {/* Real-time Progress Display */}
      {loading && (
        <Box sx={{ mt: 3, mb: 3 }}>
          <Paper sx={{ p: 2, bgcolor: 'primary.light' }}>
            <Typography variant="h6" gutterBottom color="white">
              Processing...
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={progress} 
              sx={{ mb: 2, height: 8, borderRadius: 4 }}
            />
            {currentStep && (
              <Box>
                <Typography variant="body2" color="white" gutterBottom>
                  Current step: {currentStep}
                </Typography>
                <Typography variant="caption" color="white">
                  Progress: {progress}% | Completed steps: {completedSteps.length}
                </Typography>
              </Box>
            )}
          </Paper>
        </Box>
      )}
      
      {/* Completed Steps History */}
      {!loading && completedSteps.length > 0 && (
        <Box sx={{ mt: 2, mb: 2 }}>
          <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
            <Typography variant="h6" gutterBottom>
              Processing Steps Completed
            </Typography>
            <List dense>
              {completedSteps.map((step, index) => (
                <ListItem key={index} sx={{ py: 0.5 }}>
                  <ListItemText 
                    primary={step}
                    primaryTypographyProps={{ 
                      variant: 'body2',
                      color: 'text.secondary'
                    }}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
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
