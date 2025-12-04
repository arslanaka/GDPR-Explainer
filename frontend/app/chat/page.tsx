'use client';

import { useState, useRef, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { streamChat } from '@/lib/api';
import { Send, User, Bot, Loader2, Settings2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import Link from 'next/link';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    type?: 'text' | 'search_results' | 'explanation';
    data?: any;
    isStreaming?: boolean;
}

export default function ChatPage() {
    const searchParams = useSearchParams();
    const initialQuery = searchParams.get('q');
    const initialModel = searchParams.get('model');

    const [input, setInput] = useState('');
    const [model, setModel] = useState(initialModel || 'openai'); // 'openai' | 'gemini'
    const [messages, setMessages] = useState<Message[]>([
        { role: 'assistant', content: 'Hello! I am your GDPR Assistant. Ask me anything about the regulation.' }
    ]);
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const processedInitialQuery = useRef(false); // Fix for duplicate initial query

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        if (initialQuery && !processedInitialQuery.current) {
            processedInitialQuery.current = true;
            handleSend(initialQuery);
        }
    }, [initialQuery]);

    const handleSend = async (queryText: string = input) => {
        if (!queryText.trim()) return;

        // Add User Message
        const userMsg: Message = { role: 'user', content: queryText };
        setMessages((prev) => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        // Create a placeholder for Assistant Message
        const assistantMsgId = Date.now();
        setMessages((prev) => [
            ...prev,
            { role: 'assistant', content: '', isStreaming: true, type: 'text' }
        ]);

        let fullContent = '';

        await streamChat(
            queryText,
            model,
            (chunk) => {
                // Accumulate content OUTSIDE of setMessages to avoid double-invocation issues in StrictMode
                if (chunk.type === 'token') {
                    fullContent += chunk.content;
                }

                setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastMsgIndex = newMessages.length - 1;
                    // Create a shallow copy of the last message to avoid mutating state directly
                    const lastMsg = { ...newMessages[lastMsgIndex] };
                    newMessages[lastMsgIndex] = lastMsg;

                    if (lastMsg.role === 'assistant' && lastMsg.isStreaming) {
                        if (chunk.type === 'token') {
                            lastMsg.content = fullContent;
                        } else if (chunk.type === 'search_results') {
                            lastMsg.type = 'search_results';
                            lastMsg.content = chunk.content;
                            lastMsg.data = chunk.results;
                            lastMsg.isStreaming = false;
                        } else if (chunk.type === 'explanation') {
                            lastMsg.type = 'explanation';
                            lastMsg.content = chunk.content;
                            lastMsg.data = chunk.related_data;
                            lastMsg.isStreaming = false;
                        } else if (chunk.type === 'sources') {
                            // Handle sources
                        } else if (chunk.type === 'error') {
                            lastMsg.content = chunk.content;
                            lastMsg.isStreaming = false;
                        }
                    }
                    return newMessages;
                });
            },
            (err) => {
                console.error(err);
                setMessages((prev) => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error.' }]);
                setLoading(false);
            },
            () => {
                setLoading(false);
                setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastMsg = newMessages[newMessages.length - 1];
                    if (lastMsg) lastMsg.isStreaming = false;
                    return newMessages;
                });
            }
        );
    };

    return (
        <div className="flex h-screen flex-col bg-slate-50">
            {/* Header */}
            <header className="flex items-center justify-between border-b bg-white px-6 py-4 shadow-sm">
                <Link href="/" className="text-xl font-bold text-blue-600">GDPR Explainer</Link>
            </header>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 md:p-6">
                <div className="mx-auto max-w-3xl space-y-6">
                    {messages.map((msg, idx) => (
                        <div
                            key={idx}
                            className={cn(
                                "flex w-full gap-4",
                                msg.role === 'user' ? "justify-end" : "justify-start"
                            )}
                        >
                            {msg.role === 'assistant' && (
                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100">
                                    <Bot className="h-5 w-5 text-blue-600" />
                                </div>
                            )}

                            <div
                                className={cn(
                                    "max-w-[80%] rounded-2xl px-5 py-3 shadow-sm",
                                    msg.role === 'user'
                                        ? "bg-blue-600 text-white"
                                        : "bg-white text-slate-800 border border-slate-100"
                                )}
                            >
                                <div className="whitespace-pre-wrap leading-relaxed">
                                    {msg.content}
                                    {msg.isStreaming && <span className="inline-block w-1.5 h-4 ml-1 bg-blue-400 animate-pulse align-middle"></span>}
                                </div>

                                {/* Render Search Results */}
                                {msg.type === 'search_results' && msg.data && (
                                    <div className="mt-4 space-y-2">
                                        {msg.data.map((res: any, i: number) => (
                                            <Link key={i} href={`/article/${res.id}`} className="block rounded border p-3 hover:bg-slate-50 transition-colors">
                                                <div className="font-semibold text-blue-600">Article {res.article_number}: {res.title}</div>
                                                <div className="text-xs text-slate-500 mt-1 line-clamp-2">{res.text_snippet}</div>
                                            </Link>
                                        ))}
                                    </div>
                                )}

                                {/* Render Explanation Link */}
                                {msg.type === 'explanation' && msg.data && (
                                    <div className="mt-4">
                                        <Link href={`/article/${msg.data.id}`} className="inline-flex items-center text-sm font-medium text-blue-600 hover:underline">
                                            View Full Article & Graph →
                                        </Link>
                                    </div>
                                )}
                            </div>

                            {msg.role === 'user' && (
                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-200">
                                    <User className="h-5 w-5 text-slate-600" />
                                </div>
                            )}
                        </div>
                    ))}

                    {loading && messages[messages.length - 1].role !== 'assistant' && (
                        <div className="flex w-full justify-start gap-4">
                            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100">
                                <Bot className="h-5 w-5 text-blue-600" />
                            </div>
                            <div className="bg-white text-slate-800 border border-slate-100 max-w-[80%] rounded-2xl px-5 py-3 shadow-sm">
                                <div className="flex space-x-1 h-6 items-center">
                                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input Area */}
            <div className="border-t bg-white p-4">
                <div className="mx-auto max-w-3xl">
                    <form
                        onSubmit={(e) => {
                            e.preventDefault();
                            handleSend();
                        }}
                        className="relative flex items-center gap-2"
                    >
                        {/* Model Selector */}
                        <div className="flex items-center space-x-1 bg-white border-2 border-blue-100 rounded-full p-1 shrink-0 shadow-sm">
                            <button
                                type="button"
                                onClick={() => setModel('openai')}
                                className={cn(
                                    "px-3 py-2 rounded-full text-xs font-bold transition-all",
                                    model === 'openai' ? "bg-blue-600 text-white shadow-md" : "text-slate-500 hover:text-slate-700 hover:bg-slate-100"
                                )}
                            >
                                GPT-4
                            </button>
                            <button
                                type="button"
                                onClick={() => setModel('gemini')}
                                className={cn(
                                    "px-3 py-2 rounded-full text-xs font-bold transition-all",
                                    model === 'gemini' ? "bg-blue-600 text-white shadow-md" : "text-slate-500 hover:text-slate-700 hover:bg-slate-100"
                                )}
                            >
                                Gemini
                            </button>
                        </div>

                        <div className="relative flex-1">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder={`Ask a question...`}
                                className="block w-full rounded-full border-0 bg-slate-100 py-4 pl-6 pr-14 text-slate-900 shadow-inner focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                                disabled={loading}
                            />
                            <button
                                type="submit"
                                disabled={loading || !input.trim()}
                                className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full bg-blue-600 p-2 text-white hover:bg-blue-500 disabled:opacity-50"
                            >
                                <Send className="h-5 w-5" />
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
