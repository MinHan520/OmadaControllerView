import React, { useState, useEffect, useRef } from 'react';
import './Chatbot.css';

const TypingIndicator = () => (
    <div className="message bot">
        <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </div>
);

const Chatbot = ({ ngrokUrl, token, isVisible, onClose }) => {
    const [messages, setMessages] = useState([
        { text: 'Hello there! I am your Omada Controller Assistant. How can I help you today?', sender: 'bot' },
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages, isTyping]);

    const handleSendMessage = async (e) => {
        if (e.key && e.key !== 'Enter') return;
        if (!inputValue.trim()) return;

        const newMessages = [...messages, { text: inputValue, sender: 'user' }];
        setMessages(newMessages);
        setInputValue('');
        setIsTyping(true);

        try {
            // const response = await fetch(`${ngrokUrl}/chatbot`, { // Uncomment when backend is ready
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json',
            //         'Authorization': `Bearer ${token}`,
            //         'ngrok-skip-browser-warning': 'true',
            //     },
            //     body: JSON.stringify({ message: inputValue }),
            // });

            // const data = await response.json();

            // --- Mock Response (for now) ---
            await new Promise(resolve => setTimeout(resolve, 1500));
            const data = { reply: "That's an excellent question! I'm currently set up with placeholder data, but I'm learning more every day. Soon, I'll be able to give you detailed information about your Omada Controller. Is there anything else I can help you with?" };
            // --- End Mock Response ---

            setMessages(currentMessages => [...currentMessages, { text: data.reply, sender: 'bot' }]);
        } catch (error) {
            console.error("Error sending message to chatbot backend:", error);
            setMessages(currentMessages => [...currentMessages, { text: "I seem to be having a little trouble connecting. Please try again in a moment.", sender: 'bot' }]);
        } finally {
            setIsTyping(false);
        }
    };

    if (!isVisible) return null;

    return (
        <div className="chatbot-popup">
            <div className="chatbot-header">
                <span>Omada Assistant</span>
                <button onClick={onClose} className="close-btn">×</button>
            </div>
            <div className="chatbot-messages">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.sender}`}>
                        {msg.text}
                    </div>
                ))}
                {isTyping && <TypingIndicator />}
                <div ref={messagesEndRef} />
            </div>
            <div className="chatbot-input-container">
                <input
                    type="text"
                    className="chatbot-input"
                    placeholder="Ask me anything..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleSendMessage}
                />
                <button className="send-btn" onClick={handleSendMessage}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                </button>
            </div>
        </div>
    );
};

export default Chatbot;
