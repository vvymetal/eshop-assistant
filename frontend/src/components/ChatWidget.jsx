import React, { useState, useEffect, useRef } from 'react';
import DOMPurify from 'dompurify';
import './ChatWidget.css';

const ChatWidget = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationContext, setConversationContext] = useState([]);
  const [suggestedProducts, setSuggestedProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const chatMessagesRef = useRef(null);
  const eventSourceRef = useRef(null);

  // Funkce formatMessage zůstává beze změny

  const scrollToBottom = () => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;
    await sendMessage(userInput);
  };

  const sendMessage = async (message, isRetry = false) => {
    setLoading(true);
    setError(null);

    if (!isRetry) {
      const newUserMessage = { role: 'user', content: message };
      setMessages(prevMessages => [...prevMessages, newUserMessage]);
      setConversationContext(prevContext => [...prevContext, newUserMessage]);
      setUserInput('');
    }

    // Uzavřeme předchozí EventSource, pokud existuje
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const queryParams = new URLSearchParams({
      message: message,
      context: JSON.stringify(conversationContext)
    }).toString();

    eventSourceRef.current = new EventSource(`/chat?${queryParams}`);
    let assistantResponse = '';

    setMessages(prevMessages => [...prevMessages, { role: 'assistant', content: '' }]);

    eventSourceRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        assistantResponse += data.content;

        setMessages(prevMessages => {
          const newMessages = [...prevMessages];
          newMessages[newMessages.length - 1].content = formatMessage(assistantResponse);
          return newMessages;
        });

        scrollToBottom();
      } catch (e) {
        console.error('Error parsing SSE data:', e);
      }
    };

    eventSourceRef.current.onerror = (error) => {
      console.error('EventSource failed:', error);
      setError('Omlouváme se, došlo k chybě při komunikaci s asistentem. Zkuste to prosím znovu za chvíli.');
      setMessages(prevMessages => prevMessages.filter(msg => msg.role !== 'assistant' || msg.content !== ''));
      setLoading(false);
      eventSourceRef.current.close();
    };

    eventSourceRef.current.onopen = () => {
      setLoading(true);
    };

    eventSourceRef.current.addEventListener('done', (event) => {
      setConversationContext(prevContext => [
        ...prevContext,
        { role: 'assistant', content: assistantResponse }
      ]);
      setLoading(false);
      eventSourceRef.current.close();
    });
  };

  const handleRetry = () => {
    const lastUserMessage = messages.findLast(msg => msg.role === 'user');
    if (lastUserMessage) {
      sendMessage(lastUserMessage.content, true);
    }
  };

  useEffect(() => {
    scrollToBottom();
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [messages]);

  // Zbytek komponenty (return statement) zůstává beze změny

};

export default ChatWidget;