import React, { useState } from 'react';
import { Container, Typography, TextField, Box, CircularProgress, Paper, List, Alert, Chip, IconButton, InputAdornment } from '@mui/material';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import TimelineProgress from '../components/TimelineProgress';
import ArticleCard from '../components/ArticleCard';
import RagAnswer from '../components/RagAnswer';
import { getApiUrl, API_ENDPOINTS } from '../config';

const RagQaPage = ({
  question,
  setQuestion,
  answer,
  setAnswer,
  loading,
  setLoading,
  error,
  setError,
  completedSteps,
  setCompletedSteps,
  currentStep,
  setCurrentStep,
  translationInfo,
  setTranslationInfo
}) => {
  const [inputError, setInputError] = useState(false);

  const ragSteps = [
    { id: 'detect', label: 'Detecting non-English characters' },
    { id: 'translate', label: 'Translating to English' },
    { id: 'expand', label: 'Expanding query for better search' },
    { id: 'embedding', label: 'Generating query embeddings' },
    { id: 'search', label: 'Searching relevant articles' },
    { id: 'retrieve', label: 'Retrieving articles' },
    { id: 'context', label: 'Building context' },
    { id: 'generate', label: 'Generating AI answer' },
    { id: 'complete', label: 'RAG analysis completed' }
  ];

  // RAG examples for Try Asking section
  const ragExamples = [
    "How does health insurance affect patient outcomes?",
    "What are the latest Medicare policy changes?",
    "How do insurance networks impact healthcare access?"
  ];

  const handleRagQuestion = async () => {
    if (!question.trim()) {
      setInputError(true);
      return;
    }
    setInputError(false);
    
    // Reset all states at the beginning
    setLoading(true);
    setError('');
    setAnswer(null);
    setCurrentStep('');
    setCompletedSteps([]);
    setTranslationInfo(null);
    
    // Force a small delay to ensure state updates are processed
    await new Promise(resolve => setTimeout(resolve, 100));

    try {
      const response = await fetch(getApiUrl(API_ENDPOINTS.RAG_QA_WITH_PROGRESS), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', },
        body: JSON.stringify({ question, top_k: 20 })
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
            console.log('SSE line:', line); // Log every SSE line for debugging
            try {
              const data = JSON.parse(line.slice(6));

              if (data.error) {
                setError(data.error);
                setLoading(false);
                return;
              }

              if (data.step) {
                setCurrentStep(data.step);
                setCompletedSteps(prev => {
                  if (!prev.includes(data.step)) {
                    return [...prev, data.step];
                  }
                  return prev;
                });
                
                if (data.translation_info) {
                  setTranslationInfo({ 
                    original: data.translation_info.replace('Original: ', ''), 
                    step: data.step 
                  });
                }
                if (data.translation_result) {
                  setTranslationInfo(prev => ({ 
                    ...prev, 
                    translated: data.translation_result.replace('Translated: ', ''), 
                    step: data.step 
                  }));
                }
              }

              if (data.complete) {
                setAnswer(data);
                setLoading(false);
                return;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e, line);
              // Don't continue here, just log the error and skip this line
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
            setAnswer(data);
            setLoading(false);
            return;
          }
        } catch (e) {
          console.error('Error parsing final buffer data:', e, buffer);
        }
      }
      
    } catch (err) {
      console.error('RAG QA error:', err);
      setError(err.message || 'RAG QA failed');
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ px: { xs: 1, sm: 2, md: 3 } }}>
      <Typography 
        variant="h4" 
        sx={{ 
          mb: 1,
          fontSize: { xs: '1.5rem', sm: '2rem', md: '2.125rem' },
          fontWeight: 600
        }}
      >
        RAG Question Answering
      </Typography>
      <Typography 
        variant="subtitle1" 
        color="text.secondary" 
        sx={{ 
          mb: 3,
          fontSize: { xs: '0.875rem', sm: '1rem' },
          lineHeight: 1.5
        }}
      >
        Currently supporting research on the healthcare system using PubMed resources.
        Future updates will include more databases for more powerful searches.
      </Typography>
      
      <Paper sx={{ p: { xs: 2, sm: 3 }, mb: 3 }}>
        <TextField
            label="Ask a question"
            variant="outlined"
            fullWidth
            multiline
            rows={4}
            value={question}
            onChange={(e) => {
              setQuestion(e.target.value);
              if (inputError) {
                setInputError(false);
              }
            }}
            placeholder="e.g., How does health insurance affect patient outcomes? What are the latest Medicare policy changes?"
            error={inputError}
            helperText={inputError ? "Please enter a question" : ""}
            sx={{
                '& .MuiOutlinedInput-root': {
                    position: 'relative',
                    pr: '14px' // Keep default padding
                },
                '& .MuiInputLabel-root': {
                  fontSize: { xs: '0.875rem', sm: '1rem' }
                },
                '& .MuiInputBase-input': {
                  fontSize: { xs: '0.875rem', sm: '1rem' }
                }
            }}
            InputProps={{
                endAdornment: (
                    <InputAdornment position="end" sx={{ position: 'absolute', bottom: 16, right: 16 }}>
                        <IconButton
                            onClick={handleRagQuestion}
                            disabled={loading}
                            sx={{
                                width: { xs: '36px', sm: '40px' },
                                height: { xs: '36px', sm: '40px' },
                                transition: 'all 0.3s ease',
                                backgroundColor: question.trim() ? '#000000' : '#f0f0f0',
                                color: question.trim() ? '#ffffff' : '#666666',
                                '&:hover': {
                                    backgroundColor: question.trim() ? '#333333' : '#e0e0e0',
                                    transform: 'scale(1.1)'
                                }
                            }}
                            aria-label="Ask question"
                        >
                            {loading ? (
                                <CircularProgress size={20} color="inherit" />
                            ) : (
                                <ArrowUpwardIcon sx={{ fontSize: { xs: '1.2rem', sm: '1.5rem' } }} />
                            )}
                        </IconButton>
                    </InputAdornment>
                )
            }}
        />
        
        {/* Try Asking section */}
        <Box sx={{ mt: 3, pt: 3, borderTop: '1px solid #e0e0e0' }}>
          <Typography 
            variant="subtitle2" 
            color="text.secondary" 
            sx={{ 
              mb: 3, 
              fontWeight: 500,
              fontSize: { xs: '0.875rem', sm: '1rem' }
            }}
          >
            Try asking:
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {ragExamples.map((example, index) => (
              <Chip
                key={index}
                label={example}
                variant="outlined"
                clickable
                onClick={() => setQuestion(example)}
                sx={{ 
                  justifyContent: 'flex-start',
                  textAlign: 'left',
                  height: 'auto',
                  px: { xs: 2, sm: 3 },
                  py: { xs: 1, sm: 1.5 },
                  fontSize: { xs: '0.8rem', sm: '0.9rem' },
                  '& .MuiChip-label': {
                    whiteSpace: 'normal',
                    lineHeight: 1.5,
                    padding: { xs: '6px 0', sm: '8px 0' }
                  },
                  '&:hover': { 
                    backgroundColor: 'primary.light',
                    color: 'primary.dark',
                    transform: 'translateX(4px)',
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
            steps={ragSteps}
            completedSteps={completedSteps}
            currentStep={currentStep}
            isLoading={loading}
            translationInfo={translationInfo}
        />
      )}

      {answer && (
        <Box sx={{ mt: 4 }}>
          <RagAnswer answer={answer.answer} relevantArticles={answer.relevant_articles} />
          <Typography 
            variant="h5" 
            gutterBottom 
            sx={{ 
              mt: 4,
              fontSize: { xs: '1.25rem', sm: '1.5rem' },
              fontWeight: 600
            }}
          >
            Supporting Articles ({answer.relevant_articles.length})
          </Typography>
          <List>
            {answer.relevant_articles.map((item) => (
              <ArticleCard key={item.pmid} article={item} />
            ))}
          </List>
        </Box>
      )}

      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
    </Container>
  );
};

export default RagQaPage; 