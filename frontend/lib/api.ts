import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface SearchResult {
    id: string;
    article_number: number;
    title: string;
    text_snippet: string;
    score: number;
}

export interface ArticleDetail {
    id: string;
    number: number;
    title: string;
    obligations: { summary: string; role: string }[];
    terms: { term: string; definition: string }[];
    topics: string[];
    references: { id: string; number: number }[];
}

export interface Explanation {
    article_id: string;
    explanation: string;
    context: ArticleDetail;
}

export const searchArticles = async (query: string): Promise<SearchResult[]> => {
    const response = await api.get<{ results: SearchResult[] }>('/search', { params: { q: query } });
    return response.data.results;
};

export const getArticle = async (id: string): Promise<ArticleDetail> => {
    const response = await api.get<ArticleDetail>(`/articles/${id}`);
    return response.data;
};

export const explainArticle = async (id: string): Promise<Explanation> => {
    const response = await api.get<Explanation>(`/explain/${id}`);
    return response.data;
};

// Streaming Chat Helper
export const streamChat = async (
    query: string,
    model: string,
    onChunk: (chunk: any) => void,
    onError: (err: any) => void,
    onComplete: () => void
) => {
    try {
        const response = await fetch('http://localhost:8000/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query, model }),
        });

        if (!response.body) return;

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');

            // Process all complete lines
            buffer = lines.pop() || ''; // Keep the last incomplete line in buffer

            for (const line of lines) {
                if (line.trim()) {
                    try {
                        const json = JSON.parse(line);
                        onChunk(json);
                    } catch (e) {
                        console.error('Error parsing JSON chunk', e);
                    }
                }
            }
        }

        onComplete();
    } catch (err) {
        onError(err);
    }
};

export const chatWithGDPR = async (query: string, model: string = 'openai'): Promise<any> => {
    return new Promise((resolve, reject) => {
        let finalResult: any = { content: '' };

        streamChat(
            query,
            model,
            (chunk) => {
                if (chunk.type === 'token') {
                    finalResult.content += chunk.content;
                    finalResult.type = 'answer';
                } else {
                    finalResult = { ...finalResult, ...chunk };
                }
            },
            (err) => reject(err),
            () => resolve(finalResult)
        );
    });
};

export default api;
