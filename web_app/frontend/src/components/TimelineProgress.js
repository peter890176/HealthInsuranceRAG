import React, { useState } from 'react';
import { Box, Stepper, Step, StepLabel, StepConnector, Typography, CircularProgress, Paper, Chip, Button, LinearProgress } from '@mui/material';
import { styled } from '@mui/material/styles';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import TranslateIcon from '@mui/icons-material/Translate';
import GavelIcon from '@mui/icons-material/Gavel';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

const QontoConnector = styled(StepConnector)(({ theme }) => ({
  '& .MuiStepConnector-line': {
    borderColor: theme.palette.mode === 'dark' ? theme.palette.grey[800] : '#eaeaf0',
    borderTopWidth: 3,
    borderRadius: 1,
  },
}));

const TimelineProgress = ({ steps, completedSteps, currentStep, isLoading, translationInfo }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Ensure completedSteps is always an array
  const safeCompletedSteps = Array.isArray(completedSteps) ? completedSteps : [];
  const activeStepIndex = safeCompletedSteps.indexOf(currentStep);
  const completedCount = safeCompletedSteps.length;
  const totalSteps = steps.length;
  
  // Find current step label
  const currentStepData = steps.find(step => step.id === currentStep);
  const currentStepLabel = currentStepData ? currentStepData.label : '';
  
  return (
    <Paper sx={{ p: { xs: 2, sm: 3 }, mb: 3 }}>
      {!isExpanded ? (
        // Collapsed view - compact progress display
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography 
              variant="subtitle1" 
              sx={{ 
                fontWeight: 600,
                fontSize: { xs: '0.875rem', sm: '1rem' }
              }}
            >
              Search Progress
            </Typography>
            <Button
              size="small"
              onClick={() => setIsExpanded(true)}
              endIcon={<ExpandMoreIcon />}
              sx={{ 
                textTransform: 'none',
                fontSize: { xs: '0.75rem', sm: '0.875rem' }
              }}
            >
              Show Details
            </Button>
          </Box>
          
          {/* Progress bar */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography 
                variant="body2" 
                color="text.secondary"
                sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
              >
                {completedCount} of {totalSteps} steps completed
              </Typography>
              <Typography 
                variant="body2" 
                sx={{ 
                  fontWeight: 600,
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  color: '#000000'
                }}
              >
                {Math.round((completedCount / totalSteps) * 100)}%
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={(completedCount / totalSteps) * 100}
              sx={{ 
                height: 8, 
                borderRadius: 4,
                backgroundColor: '#f0f0f0',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: '#000000',
                  borderRadius: 4
                }
              }}
            />
          </Box>
          
          {/* Current step display */}
          {currentStep && (
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              p: 1.5, 
              bgcolor: '#f5f5f5', 
              borderRadius: 1,
              border: '1px solid',
              borderColor: '#000000'
            }}>
              <CircularProgress size={16} sx={{ mr: 1.5, color: '#000000' }} />
              <Typography 
                variant="body2"
                sx={{ 
                  fontWeight: 500,
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  color: '#000000'
                }}
              >
                {currentStepLabel}
              </Typography>
            </Box>
          )}
          
          {/* Translation info in collapsed view */}
          {translationInfo && (
            <Box sx={{ mt: 2, p: 1.5, bgcolor: '#f5f5f5', borderRadius: 1 }}>
              <Box display="flex" alignItems="center" mb={1}>
                <TranslateIcon fontSize="small" sx={{ mr: 1, color: '#000000' }}/>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    fontSize: { xs: '0.7rem', sm: '0.75rem' },
                    color: '#333333'
                  }}
                >
                  Translation: "{translationInfo.original}" → "{translationInfo.translated}"
                </Typography>
              </Box>
            </Box>
          )}
        </Box>
      ) : (
        // Expanded view - full vertical timeline
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography 
              variant="subtitle1" 
              sx={{ 
                fontWeight: 600,
                fontSize: { xs: '0.875rem', sm: '1rem' }
              }}
            >
              Detailed Progress
            </Typography>
            <Button
              size="small"
              onClick={() => setIsExpanded(false)}
              endIcon={<ExpandLessIcon />}
              sx={{ 
                textTransform: 'none',
                fontSize: { xs: '0.75rem', sm: '0.875rem' }
              }}
            >
              Hide Details
            </Button>
          </Box>
          
          <Stepper 
            alternativeLabel={false}
            activeStep={activeStepIndex} 
            connector={<QontoConnector />}
            orientation="vertical"
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
                      if (isCompleted) {
                        return <CheckCircleIcon sx={{ 
                          fontSize: { xs: '20px', sm: '24px' },
                          color: '#000000'
                        }} />;
                      }
                      if (isActive && !isCompleted) {
                        return <CircularProgress size={20} sx={{ color: '#000000' }} />;
                      }
                      return (
                        <Box sx={{ 
                          color: '#666666', 
                          border: '2px solid #666666', 
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
                        color: isActive ? '#000000' : '#333333'
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
                  bgcolor: '#f5f5f5' 
                }}
              >
                  <Box display="flex" alignItems="center" mb={1}>
                      <TranslateIcon fontSize="small" sx={{ mr: 1, color: '#000000' }}/>
                      <Typography 
                        variant="subtitle2" 
                        sx={{ 
                          fontSize: { xs: '0.8rem', sm: '0.875rem' },
                          color: '#333333'
                        }}
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
                      color: '#666666',
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
                      wordBreak: 'break-word',
                      color: '#000000'
                    }}
                  >
                    "{translationInfo.translated}"
                  </Typography>
                </Box>
            </Paper>
          )}
        </Box>
      )}
    </Paper>
  );
};

export default TimelineProgress; 