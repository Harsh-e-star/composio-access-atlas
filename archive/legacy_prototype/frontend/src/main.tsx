import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

function mount() {
  const rootEl = document.getElementById('root');
  if (rootEl) {
    ReactDOM.createRoot(rootEl).render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
  } else {
    window.addEventListener('DOMContentLoaded', mount);
  }
}

mount();
