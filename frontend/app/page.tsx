'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Search, ArrowRight, MessageSquare } from 'lucide-react';
import { chatWithGDPR } from '@/lib/api';

export default function Home() {
  const [query, setQuery] = useState('');
  const [model, setModel] = useState('openai'); // 'openai' | 'gemini'
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      // For now, simple search redirects to search results page (to be built)
      // Or we can use the chat API directly here for a "Ask anything" experience
      const response = await chatWithGDPR(query);

      if (response.type === 'explanation' && response.related_data) {
        // Redirect to article page if it's an explanation
        router.push(`/article/${response.related_data.id}`);
      } else {
        // For general QA or search results, we might want a search page
        // For this MVP, let's just log it or show a simple alert, 
        // but better: redirect to a /chat page with the query pre-filled
        // For general QA or search results, we might want a search page
        // For this MVP, let's just log it or show a simple alert, 
        // but better: redirect to a /chat page with the query pre-filled
        router.push(`/chat?q=${encodeURIComponent(query)}&model=${model}`);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-slate-50 to-slate-100 p-4 text-slate-900">
      <div className="w-full max-w-3xl space-y-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-5xl font-bold tracking-tight sm:text-7xl bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
            GDPR Explainer
          </h1>
          <p className="mt-6 text-lg leading-8 text-slate-600">
            Navigate the General Data Protection Regulation with AI.
            <br />
            Ask questions, explore the knowledge graph, and get instant explanations.
          </p>
        </motion.div>



        {/* Model Selector */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="flex justify-center mb-6"
        >
          <div className="flex items-center space-x-1 bg-white border-2 border-blue-100 rounded-full p-1 shadow-sm">
            <button
              onClick={() => setModel('openai')}
              className={`px-4 py-2 rounded-full text-sm font-bold transition-all ${model === 'openai' ? "bg-blue-600 text-white shadow-md" : "text-slate-500 hover:text-slate-700 hover:bg-slate-50"
                }`}
            >
              GPT-4
            </button>
            <button
              onClick={() => setModel('gemini')}
              className={`px-4 py-2 rounded-full text-sm font-bold transition-all ${model === 'gemini' ? "bg-blue-600 text-white shadow-md" : "text-slate-500 hover:text-slate-700 hover:bg-slate-50"
                }`}
            >
              Gemini
            </button>
          </div>
        </motion.div>

        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          onSubmit={handleSearch}
          className="relative mx-auto mt-10 max-w-xl"
        >
          <div className="relative">
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
              <Search className="h-5 w-5 text-slate-400" aria-hidden="true" />
            </div>
            <input
              type="text"
              className="block w-full rounded-full border-0 py-4 pl-11 pr-4 text-slate-900 shadow-xl ring-1 ring-inset ring-slate-200 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
              placeholder="Ask a question (e.g., 'Explain Article 32' or 'What are the fines?')"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
            />
            <div className="absolute inset-y-0 right-0 flex items-center pr-2">
              <button
                type="submit"
                disabled={loading}
                className="inline-flex items-center gap-x-2 rounded-full bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:opacity-50"
              >
                {loading ? 'Thinking...' : <ArrowRight className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </motion.form>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-10 flex justify-center gap-x-6"
        >
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {['Explain Article 6', 'What is a Data Controller?', 'Fines for non-compliance'].map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => {
                  setQuery(suggestion);
                  // Optional: auto-submit
                }}
                className="rounded-lg bg-white px-4 py-3 text-sm font-semibold text-slate-900 shadow-sm ring-1 ring-inset ring-slate-200 hover:bg-slate-50"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </motion.div>
      </div>
    </main >
  );
}
