import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import ScienceIcon from '@mui/icons-material/Science';

const Header = () => {
  return (
    <AppBar 
      position="fixed" 
      sx={{ 
        zIndex: (theme) => theme.zIndex.drawer + 1,
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        backdropFilter: 'blur(8px)',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        color: 'text.primary'
      }}
    >
      <Toolbar>
        <ScienceIcon sx={{ mr: 2, color: 'primary.main' }} />
        <Box>
          <Typography variant="h6" noWrap component="div">
            Evidence-based Search Station
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header; 