'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getArticle, explainArticle, ArticleDetail, Explanation } from '@/lib/api';
import GraphViz from '@/components/graph/GraphViz';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { Loader2, BookOpen, Share2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function ArticlePage() {
    const params = useParams();
    const id = params.id as string;

    const [article, setArticle] = useState<ArticleDetail | null>(null);
    const [explanation, setExplanation] = useState<Explanation | null>(null);
    const [loading, setLoading] = useState(true);
    const [explaining, setExplaining] = useState(true);

    useEffect(() => {
        if (!id) return;

        const fetchData = async () => {
            try {
                // 1. Fetch Basic Data (Graph)
                const data = await getArticle(id);
                setArticle(data);
                setLoading(false);

                // 2. Fetch AI Explanation (Parallel but slower)
                const exp = await explainArticle(id);
                setExplanation(exp);
            } catch (error) {
                console.error('Failed to fetch article', error);
            } finally {
                setLoading(false);
                setExplaining(false);
            }
        };

        fetchData();
    }, [id]);

    if (loading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
            </div>
        );
    }

    if (!article) {
        return <div className="p-10 text-center">Article not found.</div>;
    }

    return (
        <div className="min-h-screen bg-slate-50 p-4 md:p-8">
            <div className="mx-auto max-w-6xl space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <Link href="/" className="flex items-center text-slate-500 hover:text-slate-900">
                        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Search
                    </Link>
                    <h1 className="text-2xl font-bold text-slate-900">Article {article.number}: {article.title}</h1>
                    <button className="rounded-full p-2 hover:bg-slate-200">
                        <Share2 className="h-5 w-5 text-slate-600" />
                    </button>
                </div>

                <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
                    {/* Left Column: Explanation & Text */}
                    <div className="space-y-6 lg:col-span-2">
                        {/* AI Explanation Card */}
                        <Card className="border-blue-100 bg-white shadow-md">
                            <CardHeader className="bg-gradient-to-r from-blue-50 to-white pb-4">
                                <CardTitle className="flex items-center text-blue-700">
                                    <BookOpen className="mr-2 h-5 w-5" />
                                    AI Explanation
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="pt-6">
                                {explaining ? (
                                    <div className="flex items-center space-x-2 text-slate-500">
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                        <span>Generating simplified explanation...</span>
                                    </div>
                                ) : explanation ? (
                                    <div className="prose prose-slate max-w-none">
                                        <div className="whitespace-pre-line text-slate-700 leading-relaxed">
                                            {explanation.explanation}
                                        </div>
                                    </div>
                                ) : (
                                    <div className="text-red-500">Failed to load explanation.</div>
                                )}
                            </CardContent>
                        </Card>

                        {/* Obligations List */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Key Obligations</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {article.obligations.length > 0 ? (
                                    <ul className="space-y-3">
                                        {article.obligations.map((obl, i) => (
                                            <li key={i} className="flex items-start rounded-lg border p-3 bg-slate-50">
                                                <span className="mr-2 mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">
                                                    {i + 1}
                                                </span>
                                                <div>
                                                    <span className="font-semibold text-slate-900">{obl.role}: </span>
                                                    <span className="text-slate-600">{obl.summary}</span>
                                                </div>
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p className="text-slate-500">No specific obligations extracted.</p>
                                )}
                            </CardContent>
                        </Card>
                    </div>

                    {/* Right Column: Graph & Metadata */}
                    <div className="space-y-6">
                        {/* Knowledge Graph */}
                        <Card className="overflow-hidden">
                            <CardHeader>
                                <CardTitle>Knowledge Graph</CardTitle>
                            </CardHeader>
                            <div className="border-t">
                                <GraphViz data={article} />
                            </div>
                        </Card>

                        {/* Defined Terms */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Defined Terms</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {article.terms.length > 0 ? (
                                    <div className="flex flex-wrap gap-2">
                                        {article.terms.map((term, i) => (
                                            <div key={i} className="group relative cursor-help rounded-full bg-purple-100 px-3 py-1 text-xs font-medium text-purple-700 hover:bg-purple-200">
                                                {term.term}
                                                {/* Simple Tooltip */}
                                                <div className="absolute bottom-full left-1/2 mb-2 hidden w-48 -translate-x-1/2 rounded bg-slate-800 p-2 text-xs text-white shadow-lg group-hover:block z-10">
                                                    {term.definition}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-slate-500 text-sm">No terms defined in this article.</p>
                                )}
                            </CardContent>
                        </Card>

                        {/* Related Articles */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Related Articles</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {article.references.length > 0 ? (
                                    <div className="flex flex-wrap gap-2">
                                        {article.references.map((ref, i) => (
                                            <Link key={i} href={`/article/${ref.id}`} className="rounded-md border px-3 py-1 text-sm hover:bg-slate-50 text-blue-600">
                                                Art. {ref.number}
                                            </Link>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-slate-500 text-sm">No cross-references found.</p>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}
