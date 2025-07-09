import React from 'react';
import { Box, Stepper, Step, StepLabel, StepConnector, Typography, CircularProgress, Paper, Chip } from '@mui/material';
import { styled } from '@mui/material/styles';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import TranslateIcon from '@mui/icons-material/Translate';
import GavelIcon from '@mui/icons-material/Gavel';

const QontoConnector = styled(StepConnector)(({ theme }) => ({
  '& .MuiStepConnector-line': {
    borderColor: theme.palette.mode === 'dark' ? theme.palette.grey[800] : '#eaeaf0',
    borderTopWidth: 3,
    borderRadius: 1,
  },
}));

const TimelineProgress = ({ steps, completedSteps, currentStep, isLoading, translationInfo }) => {
  // Ensure completedSteps is always an array
  const safeCompletedSteps = Array.isArray(completedSteps) ? completedSteps : [];
  const activeStepIndex = safeCompletedSteps.indexOf(currentStep);
  
  return (
    <Paper sx={{ p: { xs: 2, sm: 3 }, mb: 3 }}>
      <Stepper 
        alternativeLabel={false} // Use vertical layout for better mobile experience
        activeStep={activeStepIndex} 
        connector={<QontoConnector />}
        orientation="vertical" // Force vertical layout
        sx={{
          '& .MuiStepLabel-label': {
            fontSize: { xs: '0.75rem', sm: '0.875rem' },
            lineHeight: 1.3,
            fontWeight: 500
          },
          '& .MuiStepLabel-root': {
            padding: { xs: '8px 0', sm: '12px 0' }
          },
          '& .MuiStepConnector-root': {
            marginLeft: { xs: '10px', sm: '12px' }
          },
          '& .MuiStep-root': {
            marginBottom: { xs: '8px', sm: '12px' }
          }
        }}
      >
        {steps.map((step) => {
          const isCompleted = safeCompletedSteps.includes(step.id);
          const isActive = currentStep === step.id;

          return (
            <Step key={step.id}>
              <StepLabel
                StepIconComponent={(props) => {
                  if (isCompleted && (!isLoading || !isActive)) {
                    return <CheckCircleIcon color="success" sx={{ fontSize: { xs: '20px', sm: '24px' } }} />;
                  }
                  if (isActive) {
                    return <CircularProgress size={20} />;
                  }
                  return (
                    <Box sx={{ 
                      color: 'grey.400', 
                      border: '1px solid', 
                      borderRadius: '50%', 
                      width: { xs: 20, sm: 24 }, 
                      height: { xs: 20, sm: 24 } 
                    }} />
                  );
                }}
              >
                <Typography 
                  variant="body2"
                  sx={{ 
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    lineHeight: 1.3,
                    fontWeight: isActive ? 600 : 400,
                    color: isActive ? 'primary.main' : 'text.primary'
                  }}
                >
                  {step.label}
                </Typography>
              </StepLabel>
            </Step>
          );
        })}
      </Stepper>
      {translationInfo && (
        <Paper 
          variant="outlined" 
          sx={{ 
            mt: 2, 
            p: { xs: 1.5, sm: 2 }, 
            bgcolor: 'grey.100' 
          }}
        >
            <Box display="flex" alignItems="center" mb={1}>
                <TranslateIcon fontSize="small" sx={{ mr: 1, color: 'primary.main' }}/>
                <Typography 
                  variant="subtitle2" 
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.8rem', sm: '0.875rem' } }}
                >
                  Translation Details
                </Typography>
            </Box>
            <Box sx={{ 
              display: 'flex', 
              flexDirection: { xs: 'column', sm: 'row' },
              gap: { xs: 0.5, sm: 1 },
              alignItems: { xs: 'flex-start', sm: 'center' }
            }}>
              <Chip 
                icon={<GavelIcon />} 
                label="Original" 
                size="small" 
                sx={{ 
                  fontSize: { xs: '0.7rem', sm: '0.75rem' },
                  alignSelf: { xs: 'flex-start', sm: 'center' }
                }} 
              />
              <Typography 
                variant="body2" 
                component="span" 
                sx={{ 
                  fontStyle: 'italic', 
                  color: 'text.secondary',
                  fontSize: { xs: '0.8rem', sm: '0.875rem' },
                  wordBreak: 'break-word'
                }}
              >
                "{translationInfo.original}"
              </Typography>
            </Box>
            <Box sx={{ 
              display: 'flex', 
              flexDirection: { xs: 'column', sm: 'row' },
              gap: { xs: 0.5, sm: 1 },
              alignItems: { xs: 'flex-start', sm: 'center' },
              mt: 1
            }}>
              <Chip 
                icon={<AutoAwesomeIcon />} 
                label="Translated" 
                color="primary" 
                size="small" 
                sx={{ 
                  fontSize: { xs: '0.7rem', sm: '0.75rem' },
                  alignSelf: { xs: 'flex-start', sm: 'center' }
                }} 
              />
              <Typography 
                variant="body2" 
                component="span" 
                sx={{ 
                  fontWeight: 'medium',
                  fontSize: { xs: '0.8rem', sm: '0.875rem' },
                  wordBreak: 'break-word'
                }}
              >
                "{translationInfo.translated}"
              </Typography>
            </Box>
        </Paper>
      )}
    </Paper>
  );
};

export default TimelineProgress; 