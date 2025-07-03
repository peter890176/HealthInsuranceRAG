import React, { useState } from 'react';
import { Container, Typography, TextField, Box, CircularProgress, Paper, List, Alert, Chip, IconButton, InputAdornment } from '@mui/material';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import TimelineProgress from '../components/TimelineProgress';
import ArticleCard from '../components/ArticleCard';
import RagAnswer from '../components/RagAnswer';

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
      const response = await fetch('http://localhost:5000/api/rag_qa_with_progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', },
        body: JSON.stringify({ question, top_k: 20 })
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
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (err) {
      console.error('RAG QA error:', err);
      setError(err.message || 'RAG QA failed');
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" sx={{ mb: 1 }}>RAG Question Answering</Typography>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 3 }}>
      Currently supporting research on the healthcare system using PubMed resources.
      Future updates will include more databases for more powerful searches.
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
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
                }
            }}
            InputProps={{
                endAdornment: (
                    <InputAdornment position="end" sx={{ position: 'absolute', bottom: 16, right: 16 }}>
                        <IconButton
                            onClick={handleRagQuestion}
                            disabled={loading}
                            sx={{
                                width: '40px',
                                height: '40px',
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
                                <CircularProgress size={24} color="inherit" />
                            ) : (
                                <ArrowUpwardIcon />
                            )}
                        </IconButton>
                    </InputAdornment>
                )
            }}
        />
        
        {/* Try Asking section */}
        <Box sx={{ mt: 3, pt: 3, borderTop: '1px solid #e0e0e0' }}>
          <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 3, fontWeight: 500 }}>
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
                  px: 3,
                  py: 1.5,
                  fontSize: '0.9rem',
                  '& .MuiChip-label': {
                    whiteSpace: 'normal',
                    lineHeight: 1.5,
                    padding: '8px 0'
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
          <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
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