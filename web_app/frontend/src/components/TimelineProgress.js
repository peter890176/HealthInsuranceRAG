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
  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Stepper alternativeLabel activeStep={completedSteps.indexOf(currentStep)} connector={<QontoConnector />}>
        {steps.map((step) => {
          const isCompleted = completedSteps.includes(step.id);
          const isActive = currentStep === step.id;

          return (
            <Step key={step.id}>
              <StepLabel
                StepIconComponent={(props) => {
                  if (isCompleted && (!isLoading || !isActive)) {
                    return <CheckCircleIcon color="success" />;
                  }
                  if (isActive) {
                    return <CircularProgress size={24} />;
                  }
                  return (
                    <Box sx={{ color: 'grey.400', border: '1px solid', borderRadius: '50%', width: 24, height: 24 }} />
                  );
                }}
              >
                <Typography variant="caption">{step.label}</Typography>
              </StepLabel>
            </Step>
          );
        })}
      </Stepper>
      {translationInfo && (
        <Paper variant="outlined" sx={{ mt: 2, p: 2, bgcolor: 'grey.100' }}>
            <Box display="flex" alignItems="center" mb={1}>
                <TranslateIcon fontSize="small" sx={{ mr: 1, color: 'primary.main' }}/>
                <Typography variant="subtitle2" color="text.secondary">Translation Details</Typography>
            </Box>
            <Chip icon={<GavelIcon />} label="Original" size="small" sx={{ mr: 1 }} />
            <Typography variant="body2" component="span" sx={{ fontStyle: 'italic', color: 'text.secondary' }}>
                "{translationInfo.original}"
            </Typography>
            <br />
            <Chip icon={<AutoAwesomeIcon />} label="Translated" color="primary" size="small" sx={{ mr: 1, mt: 1 }} />
            <Typography variant="body2" component="span" sx={{ fontWeight: 'medium' }}>
                "{translationInfo.translated}"
            </Typography>
        </Paper>
      )}
    </Paper>
  );
};

export default TimelineProgress; 