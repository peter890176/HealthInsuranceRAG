import React from 'react';
import { AppBar, Toolbar, Typography, Box, IconButton, useTheme, useMediaQuery } from '@mui/material';
import ScienceIcon from '@mui/icons-material/Science';
import MenuIcon from '@mui/icons-material/Menu';

const Header = ({ onMenuClick, isMobile }) => {
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

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
      <Toolbar sx={{ minHeight: { xs: '56px', sm: '64px' } }}>
        {isMobile && (
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={onMenuClick}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
        )}
        <ScienceIcon sx={{ mr: 2, color: 'primary.main' }} />
        <Box sx={{ flexGrow: 1 }}>
          <Typography 
            variant={isSmallScreen ? "subtitle1" : "h6"} 
            noWrap 
            component="div"
            sx={{ 
              fontSize: { xs: '1rem', sm: '1.25rem' },
              fontWeight: 600
            }}
          >
            {isSmallScreen ? 'Evidence Search' : 'Evidence-based Search Station'}
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header; 