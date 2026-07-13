'use client';

import { useState } from 'react';

type Message = {
  role: 'user' | 'assistant';
  text: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMessage: Message = { role: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', text: data.answer }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', text: 'Error connecting to server.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#0f2035] text-white flex flex-col items-center p-8">
      <h1 className="text-3xl font-bold mb-2">Greek Regional Resilience</h1>
      <p className="text-[#7ab8e8] mb-8">AI Research Assistant</p>

      <div className="w-full max-w-3xl flex flex-col gap-4 mb-4 h-[60vh] overflow-y-auto">
        {messages.map((m, i) => (
          <div key={i} className={`p-4 rounded-lg ${m.role === 'user' ? 'bg-[#1a3a5c] ml-16' : 'bg-[#112240] mr-16'}`}>
            <p className="text-xs text-[#7ab8e8] mb-1">{m.role === 'user' ? 'Εσύ' : 'Agent'}</p>
            <p className="whitespace-pre-wrap">{m.text}</p>
          </div>
        ))}
        {loading && <div className="p-4 bg-[#112240] rounded-lg mr-16 animate-pulse">Σκέφτομαι...</div>}
      </div>

      <div className="w-full max-w-3xl flex gap-2">
        <input
          className="flex-1 bg-[#1a3a5c] rounded-lg p-3 outline-none border border-[#2e6da4] focus:border-[#7ab8e8]"
          placeholder="Ρώτησε για μια περιφέρεια..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="bg-[#2e6da4] hover:bg-[#5b9bd5] px-6 py-3 rounded-lg font-bold transition-colors disabled:opacity-50"
        >
          Αποστολή
        </button>
      </div>
    </main>
  );
}