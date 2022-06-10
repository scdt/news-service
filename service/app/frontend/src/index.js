import React from 'react';
import ReactDOM from 'react-dom/client';
import "bulma/css/bulma.min.css";
import App from './App';
import { UserProvider } from './context/UserContext';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <UserProvider>
    <App />
  </UserProvider>
);