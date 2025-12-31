import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Send, Sparkles, Code, Zap, Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { queryApi } from '@/lib/api';

export function QueryPage() {
    const [question, setQuestion] = useState('');
    const [submittedQuestion, setSubmittedQuestion] = useState('');
    const [showCypher, setShowCypher] = useState(false);
    const [copied, setCopied] = useState(false);

    const { data: sampleQuestions } = useQuery({
        queryKey: ['sampleQuestions'],
        queryFn: () => queryApi.getSampleQuestions().then(res => res.data),
    });

    const { data: result, isLoading, error, refetch } = useQuery({
        queryKey: ['query', submittedQuestion, showCypher],
        queryFn: () =>
            queryApi.query({ question: submittedQuestion, include_cypher: showCypher }).then(res => res.data),
        enabled: !!submittedQuestion,
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (question.trim()) {
            setSubmittedQuestion(question);
            refetch();
        }
    };

    const handleSampleClick = (sample: string) => {
        setQuestion(sample);
        setSubmittedQuestion(sample);
    };

    const handleCopy = () => {
        if (result?.cypher_query) {
            navigator.clipboard.writeText(result.cypher_query);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div className="container mx-auto p-8 max-w-6xl space-y-8">
            {/* Header */}
            <div className="space-y-3">
                <div className="flex items-center gap-3">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 shadow-lg">
                        <Sparkles className="h-6 w-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                            AI-Powered Search
                        </h1>
                        <p className="text-muted-foreground mt-1">
                            Ask questions about employees, projects, and skills in natural language
                        </p>
                    </div>
                </div>
            </div>

            {/* Query Form */}
            <Card className="border-2 shadow-xl">
                <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20">
                    <CardTitle className="flex items-center gap-2">
                        <Zap className="h-5 w-5 text-purple-600" />
                        Ask a Question
                    </CardTitle>
                    <CardDescription>
                        Powered by {result?.metadata?.provider || 'AI'} · Using {result?.metadata?.model || 'LLM'}
                    </CardDescription>
                </CardHeader>
                <CardContent className="pt-6">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <Textarea
                            placeholder="e.g., Find Python experts in Engineering"
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            className="min-h-[120px] text-base resize-none focus:ring-2 focus:ring-purple-500"
                        />
                        <div className="flex items-center gap-3">
                            <Button
                                type="submit"
                                disabled={isLoading || !question.trim()}
                                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                            >
                                <Send className="mr-2 h-4 w-4" />
                                {isLoading ? 'Thinking...' : 'Ask Question'}
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => setShowCypher(!showCypher)}
                                className="border-purple-200"
                            >
                                <Code className="mr-2 h-4 w-4" />
                                {showCypher ? 'Hide' : 'Show'} Cypher
                            </Button>
                        </div>
                    </form>
                </CardContent>
            </Card>

            {/* Result */}
            {isLoading && (
                <Card className="shadow-lg">
                    <CardContent className="pt-6 space-y-3">
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-4 w-3/4" />
                        <Skeleton className="h-4 w-5/6" />
                    </CardContent>
                </Card>
            )}

            {error && (
                <Alert variant="destructive" className="shadow-lg">
                    <AlertDescription>
                        {error instanceof Error ? error.message : 'Failed to process query'}
                    </AlertDescription>
                </Alert>
            )}

            {result && (
                <Card className="shadow-xl border-2 border-purple-100">
                    <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20">
                        <div className="flex items-start justify-between">
                            <div>
                                <CardTitle className="text-xl">Answer</CardTitle>
                                <CardDescription className="mt-2">Question: {result.question}</CardDescription>
                            </div>
                            {result.metadata && (
                                <div className="flex gap-2">
                                    <Badge className="bg-purple-100 text-purple-800 border-purple-200">
                                        {result.metadata.provider}
                                    </Badge>
                                    <Badge variant="outline">{result.metadata.model}</Badge>
                                </div>
                            )}
                        </div>
                    </CardHeader>
                    <CardContent className="pt-6">
                        <div className="prose prose-slate max-w-none">
                            <p className="text-base leading-relaxed whitespace-pre-wrap">{result.answer}</p>
                        </div>

                        {showCypher && result.cypher_query && (
                            <div className="mt-6 p-5 bg-slate-900 rounded-lg relative group">
                                <div className="flex items-center justify-between mb-3">
                                    <p className="text-sm font-medium text-slate-300 flex items-center gap-2">
                                        <Code className="h-4 w-4" />
                                        Generated Cypher Query
                                    </p>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={handleCopy}
                                        className="text-slate-300 hover:text-white"
                                    >
                                        {copied ? (
                                            <Check className="h-4 w-4" />
                                        ) : (
                                            <Copy className="h-4 w-4" />
                                        )}
                                    </Button>
                                </div>
                                <pre className="text-sm text-green-400 overflow-x-auto font-mono">
                                    {result.cypher_query}
                                </pre>
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}

            {/* Sample Questions */}
            <Card className="shadow-lg">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Sparkles className="h-5 w-5 text-purple-600" />
                        Try These Questions
                    </CardTitle>
                    <CardDescription>Click any question to get started</CardDescription>
                </CardHeader>
                <CardContent>
                    {!sampleQuestions ? (
                        <div className="grid gap-2">
                            {[...Array(4)].map((_, i) => (
                                <Skeleton key={i} className="h-16 w-full" />
                            ))}
                        </div>
                    ) : sampleQuestions.length === 0 ? (
                        <p className="text-sm text-muted-foreground text-center py-4">
                            No sample questions available
                        </p>
                    ) : (
                        <div className="grid gap-2">
                            {sampleQuestions.slice(0, 6).map((sample, idx) => (
                                <Button
                                    key={idx}
                                    variant="ghost"
                                    className="justify-start text-left h-auto py-4 px-4 hover:bg-purple-50 hover:border-purple-200 border border-transparent transition-all"
                                    onClick={() => handleSampleClick(sample)}
                                >
                                    <div className="flex items-start gap-3 w-full">
                                        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-purple-100 text-xs font-medium text-purple-700">
                                            {idx + 1}
                                        </span>
                                        <span className="flex-1 text-sm">{sample}</span>
                                    </div>
                                </Button>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
