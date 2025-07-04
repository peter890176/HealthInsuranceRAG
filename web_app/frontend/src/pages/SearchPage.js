import React, { useState } from 'react';
import { Container, Typography, TextField, Box, CircularProgress, List, Paper, Chip, Alert, IconButton, InputAdornment } from '@mui/material';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import TimelineProgress from '../components/TimelineProgress';
import ArticleCard from '../components/ArticleCard';
import { getApiUrl, API_ENDPOINTS } from '../config';

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
  const [inputError, setInputError] = useState(false);

  const searchSteps = [
    { id: 'detect', label: 'Detecting non-English characters' },
    { id: 'translate', label: 'Translating to English' },
    { id: 'embedding', label: 'Generating embedding' },
    { id: 'search', label: 'Searching vector database' },
    { id: 'retrieve', label: 'Retrieving articles' },
    { id: 'complete', label: 'Search completed' }
  ];

  // Search examples for Try Asking section
  const searchExamples = [
    "health insurance coverage",
    "Medicare policy changes", 
    "healthcare costs"
  ];

  const handleSearch = async () => {
    if (!query.trim()) {
      setInputError(true);
      return;
    }
    setInputError(false);

    setLoading(true);
    setError('');
    setResults([]);
    setCurrentStep('');
    setCompletedSteps([]);
    setTranslationInfo(null);
    
    try {
      const response = await fetch(getApiUrl(API_ENDPOINTS.SEARCH_WITH_PROGRESS), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: topK })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = ''; // Buffer to handle partial chunks

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        buffer += chunk; // Add new chunk to buffer
        
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

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
              console.error('Error parsing SSE data:', e, line);
              continue;
            }
          }
        }
      }
      
      // Handle any remaining data in buffer
      if (buffer.trim() && buffer.startsWith('data: ')) {
        try {
          const data = JSON.parse(buffer.slice(6));
          if (data.complete) {
            setResults(data.results);
            setLoading(false);
            return;
          }
        } catch (e) {
          console.error('Error parsing final buffer data:', e, buffer);
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
        Find relevant medical and health insurance articles using AI-powered vector search.
        Currently supporting research on the healthcare system using PubMed resources.
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
            <TextField
                label="Enter query"
                variant="outlined"
                fullWidth
                value={query}
                onChange={(e) => {
                    setQuery(e.target.value);
                    if (inputError) setInputError(false);
                }}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="e.g., health insurance coverage, Medicare policy, healthcare costs"
                error={inputError}
                helperText={inputError ? "Please enter a query" : ""}
                sx={{ 
                    position: 'relative',
                    '& .MuiOutlinedInput-root': {
                        paddingRight: '60px' // Make space for the button
                    }
                }}
                InputProps={{
                    endAdornment: (
                        <InputAdornment position="end" sx={{ position: 'absolute', top: 16, right: 16 }}>
                            <IconButton
                                onClick={handleSearch}
                                disabled={loading}
                                sx={{
                                    width: '40px',
                                    height: '40px',
                                    transition: 'all 0.3s ease',
                                    backgroundColor: query.trim() ? '#000000' : '#f0f0f0',
                                    color: query.trim() ? '#ffffff' : '#666666',
                                    '&:hover': {
                                        backgroundColor: query.trim() ? '#333333' : '#e0e0e0',
                                        transform: 'scale(1.1)'
                                    }
                                }}
                                aria-label="Search"
                            >
                                {loading ? (
                                    <CircularProgress size={24} color="inherit" />
                                ) : (
                                    <ArrowUpwardIcon />
                                )}
                            </IconButton>
                        </InputAdornment>
                    )
                }}
            />
            <TextField
                label="Results"
                type="number"
                variant="outlined"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                sx={{ width: 120 }}
                slotProps={{ input: { min: 1, max: 50 } }}
            />
        </Box>
        
        {/* Try Asking section */}
        <Box sx={{ mt: 3, pt: 3, borderTop: '1px solid #e0e0e0' }}>
          <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2, fontWeight: 500 }}>
            Try these searches:
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            {searchExamples.map((example, index) => (
              <Chip
                key={index}
                label={example}
                variant="outlined"
                clickable
                onClick={() => setQuery(example)}
                sx={{ 
                  px: 2,
                  py: 1,
                  fontSize: '0.9rem',
                  '&:hover': { 
                    backgroundColor: 'primary.light',
                    color: 'primary.dark',
                    transform: 'translateY(-1px)',
                    transition: 'all 0.2s ease'
                  }
                }}
              />
            ))}
          </Box>
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