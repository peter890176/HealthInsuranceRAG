import React from 'react';
import { Drawer, Toolbar, List, ListItem, ListItemButton, ListItemIcon, ListItemText } from '@mui/material';
import { NavLink } from 'react-router-dom';
import SearchIcon from '@mui/icons-material/Search';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import HistoryIcon from '@mui/icons-material/History';
import SettingsIcon from '@mui/icons-material/Settings';

const drawerWidth = 240;

const navItems = [
  { text: 'Semantic Search', icon: <SearchIcon />, path: '/search' },
  { text: 'RAG QA', icon: <QuestionAnswerIcon />, path: '/rag' },
];

const futureNavItems = [
  { text: 'History', icon: <HistoryIcon />, path: '/history', disabled: true },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings', disabled: true },
]

const Sidebar = () => {
  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
      }}
    >
      <Toolbar />
      <List>
        {navItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component={NavLink}
              to={item.path}
              sx={{
                '&.active': {
                  backgroundColor: 'action.selected',
                  fontWeight: 'fontWeightBold',
                },
              }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <List sx={{ mt: 'auto' }}>
        {futureNavItems.map((item) => (
           <ListItem key={item.text} disablePadding>
             <ListItemButton disabled={item.disabled}>
               <ListItemIcon>{item.icon}</ListItemIcon>
               <ListItemText primary={item.text} secondary="Future" />
             </ListItemButton>
           </ListItem>
        ))}
      </List>
    </Drawer>
  );
};

export default Sidebar; 