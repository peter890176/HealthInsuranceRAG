import React, { useState } from 'react';
import { Container, Typography, TextField, Button, Box, CircularProgress, Paper, List, Alert } from '@mui/material';
import TimelineProgress from '../components/TimelineProgress'; // We'll create this
import ArticleCard from '../components/ArticleCard'; // We'll create this
import RagAnswer from '../components/RagAnswer'; // We'll create this

const RagQaPage = () => {
  const [question, setQuestion] = useState('');
  const [ragAnswer, setRagAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // State for progress timeline
  const [completedSteps, setCompletedSteps] = useState([]);
  const [currentStep, setCurrentStep] = useState('');
  const [translationStepInfo, setTranslationStepInfo] = useState(null);

  const ragSteps = [
    { id: 'detect', label: 'Detecting non-English characters' },
    { id: 'translate', label: 'Translating to English' },
    { id: 'embed', label: 'Generating embedding' },
    { id: 'search', label: 'Searching relevant articles' },
    { id: 'retrieve', label: 'Retrieving articles' },
    { id: 'context', label: 'Building context' },
    { id: 'generate', label: 'Generating AI answer' },
    { id: 'complete', label: 'RAG analysis completed' }
  ];

  const handleRagQuestion = async () => {
    setLoading(true);
    setError('');
    setRagAnswer(null);
    setCurrentStep('');
    setCompletedSteps([]);
    setTranslationStepInfo(null);

    try {
      const response = await fetch('http://localhost:5000/api/rag_qa_with_progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', },
        body: JSON.stringify({ question, top_k: 12 })
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
                  setTranslationStepInfo({ original: data.translation_info.replace('Original: ', ''), step: data.step });
                }
                if (data.translation_result) {
                  setTranslationStepInfo(prev => ({ ...prev, translated: data.translation_result.replace('Translated: ', ''), step: data.step }));
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

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" sx={{ mb: 1 }}>RAG Question Answering</Typography>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 3 }}>
        Get comprehensive answers from AI, backed by medical literature.
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" flexDirection="column" gap={2}>
          <TextField
            label="Ask a medical question"
            variant="outlined"
            fullWidth
            multiline
            rows={4}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., What are the latest treatments for diabetes? History of Taiwan's medical reform?"
          />
          <Button variant="contained" onClick={handleRagQuestion} disabled={loading} sx={{ alignSelf: 'flex-end' }}>
            {loading ? <CircularProgress size={24} /> : 'Ask AI'}
          </Button>
        </Box>
      </Paper>

      {(loading || completedSteps.length > 0) && (
        <TimelineProgress
            steps={ragSteps}
            completedSteps={completedSteps}
            currentStep={currentStep}
            isLoading={loading}
            translationInfo={translationStepInfo}
        />
      )}

      {ragAnswer && (
        <Box sx={{ mt: 4 }}>
          <RagAnswer answer={ragAnswer.answer} />
          <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
            Supporting Articles ({ragAnswer.relevant_articles.length})
          </Typography>
          <List>
            {ragAnswer.relevant_articles.map((item) => (
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