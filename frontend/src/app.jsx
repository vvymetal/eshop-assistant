import React from 'react';
import ChatWidget from './components/ChatWidget';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Eshop Assistant</h1>
      </header>
      <main>
        <p>Welcome to our e-shop! How can we assist you today?</p>
      </main>
      <ChatWidget />
    </div>
  );
}

export default App;