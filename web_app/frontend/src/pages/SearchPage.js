import React from 'react';
import { Container, Typography, TextField, Button, Box, CircularProgress, List, Paper, Chip, Alert } from '@mui/material';
import TimelineProgress from '../components/TimelineProgress';
import ArticleCard from '../components/ArticleCard';

const SearchPage = ({
  query,
  setQuery,
  results,
  setResults,
  loading,
  setLoading,
  error,
  setError,
  topK,
  setTopK,
  completedSteps,
  setCompletedSteps,
  currentStep,
  setCurrentStep,
  translationInfo,
  setTranslationInfo
}) => {
  
  const searchSteps = [
    { id: 'detect', label: 'Detecting non-English characters' },
    { id: 'translate', label: 'Translating to English' },
    { id: 'embedding', label: 'Generating embedding' },
    { id: 'search', label: 'Searching vector database' },
    { id: 'retrieve', label: 'Retrieving articles' },
    { id: 'complete', label: 'Search completed' }
  ];

  const handleSearch = async () => {
    setLoading(true);
    setError('');
    setResults([]);
    setCurrentStep('');
    setCompletedSteps([]);
    setTranslationInfo(null);
    
    try {
      const response = await fetch('http://localhost:5000/api/search_with_progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: topK })
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
                if (!completedSteps.includes(data.step)) {
                  setCompletedSteps(prev => [...prev, data.step]);
                }
                
                if (data.translation_info) {
                  setTranslationInfo({ original: data.translation_info.replace('Original: ', ''), step: data.step });
                }
                if (data.translation_result) {
                  setTranslationInfo(prev => ({ ...prev, translated: data.translation_result.replace('Translated: ', ''), step: data.step }));
                }
              }
              
              if (data.complete) {
                setResults(data.results);
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

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" sx={{ mb: 1 }}>Semantic Search</Typography>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 3 }}>
        Find relevant medical articles using AI-powered vector search.
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" gap={2}>
          <TextField
            label="Enter your query"
            variant="outlined"
            fullWidth
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="e.g., diabetes treatment, heart disease prevention"
          />
          <TextField
            label="Number of Results"
            type="number"
            variant="outlined"
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            sx={{ width: 140 }}
            slotProps={{ input: { min: 1, max: 50 } }}
          />
          <Button variant="contained" onClick={handleSearch} disabled={loading} sx={{ px: 4 }}>
            {loading ? <CircularProgress size={24} /> : 'Search'}
          </Button>
        </Box>
      </Paper>

      {(loading || completedSteps.length > 0) && (
        <TimelineProgress 
          steps={searchSteps}
          completedSteps={completedSteps}
          currentStep={currentStep}
          isLoading={loading}
          translationInfo={translationInfo}
        />
      )}
      
      {results.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom>
            Search Results ({results.length})
          </Typography>
          <List>
            {results.map((item) => (
              <ArticleCard key={item.pmid} article={item} />
            ))}
          </List>
        </Box>
      )}

      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
    </Container>
  );
};

export default SearchPage; 