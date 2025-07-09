import React from 'react';
import {
  Drawer,
  Toolbar,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { NavLink } from 'react-router-dom';
import SearchIcon from '@mui/icons-material/Search';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import HistoryIcon from '@mui/icons-material/History';
import SettingsIcon from '@mui/icons-material/Settings';

const drawerWidth = 240;

const navItems = [
  { text: 'RAG QA', icon: <QuestionAnswerIcon />, path: '/rag' },
  { text: 'Semantic Search', icon: <SearchIcon />, path: '/search' },
];

const futureNavItems = [
  { text: 'History', icon: <HistoryIcon />, path: '/history', disabled: true },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings', disabled: true },
]

const Sidebar = ({ mobileOpen, onDrawerToggle, isMobile }) => {
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  const drawer = (
    <>
      <Toolbar />
      <List>
        {navItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component={NavLink}
              to={item.path}
              onClick={isMobile ? onDrawerToggle : undefined}
              sx={{
                '&.active': {
                  backgroundColor: 'action.selected',
                  fontWeight: 'fontWeightBold',
                },
                py: { xs: 1.5, sm: 1 }, // Responsive padding
                px: { xs: 2, sm: 2 }, // Responsive padding
              }}
            >
              <ListItemIcon sx={{ minWidth: { xs: '40px', sm: '56px' } }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                sx={{
                  '& .MuiListItemText-primary': {
                    fontSize: { xs: '0.9rem', sm: '1rem' }
                  }
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <List sx={{ mt: 'auto' }}>
        {futureNavItems.map((item) => (
           <ListItem key={item.text} disablePadding>
             <ListItemButton
               disabled={item.disabled}
               sx={{
                 py: { xs: 1.5, sm: 1 },
                 px: { xs: 2, sm: 2 },
               }}
             >
               <ListItemIcon sx={{ minWidth: { xs: '40px', sm: '56px' } }}>
                 {item.icon}
               </ListItemIcon>
               <ListItemText
                 primary={item.text}
                 secondary="Future"
                 sx={{
                   '& .MuiListItemText-primary': {
                     fontSize: { xs: '0.9rem', sm: '1rem' }
                   }
                 }}
               />
             </ListItemButton>
           </ListItem>
        ))}
      </List>
    </>
  );

  return (
    <>
      {/* Mobile drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
        sx={{
          display: { xs: 'block', sm: 'none' }, // Updated to match new breakpoint logic
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
            backgroundColor: 'background.paper'
          },
        }}
      >
        {drawer}
      </Drawer>

      {/* Desktop drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' }, // Updated to match new breakpoint logic
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
            backgroundColor: 'background.paper'
          },
        }}
        open
      >
        {drawer}
      </Drawer>
    </>
  );
};

export default Sidebar; 