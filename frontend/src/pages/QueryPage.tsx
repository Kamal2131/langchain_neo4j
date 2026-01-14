import { useState, useRef, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Send, Sparkles, Code, Zap, Copy, Check, Radio, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Switch } from '@/components/ui/switch';
import { queryApi } from '@/lib/api';

// Confidence level colors
const confidenceColors = {
    high: 'bg-green-100 text-green-800 border-green-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    low: 'bg-red-100 text-red-800 border-red-200',
};

interface StreamingState {
    isStreaming: boolean;
    answer: string;
    expandedQuery: string | null;
    docsRetrieved: number;
    confidence: { level: string; score: number; reasons: string[] } | null;
    executionTime: number | null;
    error: string | null;
}

export function QueryPage() {
    const [question, setQuestion] = useState('');
    const [submittedQuestion, setSubmittedQuestion] = useState('');
    const [showCypher, setShowCypher] = useState(false);
    const [useStreaming, setUseStreaming] = useState(true);
    const [copied, setCopied] = useState(false);

    // Streaming state
    const [streamState, setStreamState] = useState<StreamingState>({
        isStreaming: false,
        answer: '',
        expandedQuery: null,
        docsRetrieved: 0,
        confidence: null,
        executionTime: null,
        error: null,
    });

    const eventSourceRef = useRef<EventSource | null>(null);

    const { data: sampleQuestions } = useQuery({
        queryKey: ['sampleQuestions'],
        queryFn: () => queryApi.getSampleQuestions().then(res => res.data),
    });

    // Standard (non-streaming) query
    const { data: result, isLoading, error, refetch } = useQuery({
        queryKey: ['query', submittedQuestion, showCypher],
        queryFn: () =>
            queryApi.query({ question: submittedQuestion, include_cypher: showCypher }).then(res => res.data),
        enabled: !!submittedQuestion && !useStreaming,
    });

    // Streaming query handler
    const handleStreamingQuery = useCallback((q: string) => {
        // Close existing connection
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
        }

        // Reset state
        setStreamState({
            isStreaming: true,
            answer: '',
            expandedQuery: null,
            docsRetrieved: 0,
            confidence: null,
            executionTime: null,
            error: null,
        });

        const encodedQuestion = encodeURIComponent(q);
        const evtSource = new EventSource(`/api/v1/query/stream?question=${encodedQuestion}`);
        eventSourceRef.current = evtSource;

        evtSource.addEventListener('start', () => {
            console.log('Streaming started');
        });

        evtSource.addEventListener('metadata', (e) => {
            const data = JSON.parse(e.data);
            setStreamState(prev => ({
                ...prev,
                expandedQuery: data.expanded_query || prev.expandedQuery,
                docsRetrieved: data.docs_retrieved ?? prev.docsRetrieved,
            }));
        });

        evtSource.addEventListener('token', (e) => {
            const data = JSON.parse(e.data);
            setStreamState(prev => ({
                ...prev,
                answer: prev.answer + data.token,
            }));
        });

        evtSource.addEventListener('done', (e) => {
            const data = JSON.parse(e.data);
            setStreamState(prev => ({
                ...prev,
                isStreaming: false,
                confidence: data.confidence,
                executionTime: data.execution_time_ms,
            }));
            evtSource.close();
        });

        evtSource.addEventListener('error', (e) => {
            if (e instanceof MessageEvent) {
                const data = JSON.parse(e.data);
                setStreamState(prev => ({
                    ...prev,
                    isStreaming: false,
                    error: data.error,
                }));
            }
            evtSource.close();
        });

        evtSource.onerror = () => {
            setStreamState(prev => ({
                ...prev,
                isStreaming: false,
                error: prev.answer ? null : 'Connection failed',
            }));
            evtSource.close();
        };
    }, []);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (question.trim()) {
            setSubmittedQuestion(question);
            if (useStreaming) {
                handleStreamingQuery(question);
            } else {
                refetch();
            }
        }
    };

    const handleSampleClick = (sample: string) => {
        setQuestion(sample);
        setSubmittedQuestion(sample);
        if (useStreaming) {
            handleStreamingQuery(sample);
        }
    };

    const handleCopy = () => {
        if (result?.cypher_query) {
            navigator.clipboard.writeText(result.cypher_query);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    // Determine what to display
    const displayAnswer = useStreaming ? streamState.answer : result?.answer;
    const displayConfidence = useStreaming ? streamState.confidence : result?.confidence;
    const isProcessing = useStreaming ? streamState.isStreaming : isLoading;
    const displayError = useStreaming ? streamState.error : (error instanceof Error ? error.message : null);

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
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle className="flex items-center gap-2">
                                <Zap className="h-5 w-5 text-purple-600" />
                                Ask a Question
                            </CardTitle>
                            <CardDescription>
                                Powered by {result?.metadata?.provider || 'AI'} · Using {result?.metadata?.model || 'LLM'}
                            </CardDescription>
                        </div>
                        <div className="flex items-center gap-2">
                            <Radio className={`h-4 w-4 ${useStreaming ? 'text-green-500' : 'text-gray-400'}`} />
                            <span className="text-sm text-muted-foreground">Stream</span>
                            <Switch
                                checked={useStreaming}
                                onCheckedChange={setUseStreaming}
                            />
                        </div>
                    </div>
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
                                disabled={isProcessing || !question.trim()}
                                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                            >
                                {isProcessing ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        {useStreaming ? 'Streaming...' : 'Thinking...'}
                                    </>
                                ) : (
                                    <>
                                        <Send className="mr-2 h-4 w-4" />
                                        Ask Question
                                    </>
                                )}
                            </Button>
                            {!useStreaming && (
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={() => setShowCypher(!showCypher)}
                                    className="border-purple-200"
                                >
                                    <Code className="mr-2 h-4 w-4" />
                                    {showCypher ? 'Hide' : 'Show'} Cypher
                                </Button>
                            )}
                        </div>
                    </form>
                </CardContent>
            </Card>

            {/* Streaming Progress Indicator */}
            {streamState.isStreaming && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin text-purple-600" />
                    <span>Streaming response...</span>
                    {streamState.expandedQuery && (
                        <Badge variant="outline" className="ml-2">
                            Expanded: {streamState.expandedQuery.slice(0, 50)}...
                        </Badge>
                    )}
                    {streamState.docsRetrieved > 0 && (
                        <Badge variant="outline">
                            {streamState.docsRetrieved} docs retrieved
                        </Badge>
                    )}
                </div>
            )}

            {/* Error Display */}
            {displayError && (
                <Alert variant="destructive" className="shadow-lg">
                    <AlertDescription>{displayError}</AlertDescription>
                </Alert>
            )}

            {/* Result */}
            {(displayAnswer || isProcessing) && (
                <Card className="shadow-xl border-2 border-purple-100">
                    <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20">
                        <div className="flex items-start justify-between">
                            <div>
                                <CardTitle className="text-xl flex items-center gap-2">
                                    Answer
                                    {useStreaming && streamState.isStreaming && (
                                        <span className="inline-flex h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                                    )}
                                </CardTitle>
                                <CardDescription className="mt-2">
                                    Question: {submittedQuestion}
                                </CardDescription>
                            </div>
                            <div className="flex gap-2">
                                {displayConfidence && (
                                    <Badge className={confidenceColors[displayConfidence.level as keyof typeof confidenceColors] || ''}>
                                        {displayConfidence.level} ({displayConfidence.score}%)
                                    </Badge>
                                )}
                                {streamState.executionTime && (
                                    <Badge variant="outline">
                                        {(streamState.executionTime / 1000).toFixed(1)}s
                                    </Badge>
                                )}
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className="pt-6">
                        {isProcessing && !displayAnswer ? (
                            <div className="space-y-3">
                                <Skeleton className="h-4 w-full" />
                                <Skeleton className="h-4 w-3/4" />
                                <Skeleton className="h-4 w-5/6" />
                            </div>
                        ) : (
                            <div className="prose prose-slate max-w-none">
                                <p className="text-base leading-relaxed whitespace-pre-wrap">
                                    {displayAnswer}
                                    {streamState.isStreaming && (
                                        <span className="inline-block w-2 h-5 bg-purple-500 animate-pulse ml-1" />
                                    )}
                                </p>
                            </div>
                        )}

                        {/* Confidence Reasons */}
                        {displayConfidence && displayConfidence.reasons && (
                            <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                                <p className="text-xs font-medium text-gray-500 mb-2">Confidence factors:</p>
                                <div className="flex flex-wrap gap-1">
                                    {displayConfidence.reasons.map((reason, i) => (
                                        <Badge key={i} variant="outline" className="text-xs">
                                            {reason}
                                        </Badge>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Cypher (non-streaming only) */}
                        {!useStreaming && showCypher && result?.cypher_query && (
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

                        {/* Sources (non-streaming) */}
                        {!useStreaming && result && (
                            <div className="mt-6 grid gap-4 md:grid-cols-2">
                                {/* Structured Source */}
                                <div className="p-4 bg-purple-50 dark:bg-purple-950/20 rounded-lg border border-purple-100 dark:border-purple-900">
                                    <h4 className="font-semibold text-sm text-purple-900 dark:text-purple-100 mb-2 flex items-center gap-2">
                                        <Zap className="h-4 w-4" /> Structured Source (Graph)
                                    </h4>
                                    <div className="text-xs text-muted-foreground max-h-40 overflow-y-auto whitespace-pre-wrap font-mono bg-white dark:bg-black p-2 rounded border">
                                        {typeof result.metadata?.structured_source === 'string'
                                            ? result.metadata.structured_source
                                            : JSON.stringify(result.metadata?.structured_source, null, 2) || "No structured data used."}
                                    </div>
                                </div>

                                {/* Unstructured Source */}
                                <div className="p-4 bg-pink-50 dark:bg-pink-950/20 rounded-lg border border-pink-100 dark:border-pink-900">
                                    <h4 className="font-semibold text-sm text-pink-900 dark:text-pink-100 mb-2 flex items-center gap-2">
                                        <Sparkles className="h-4 w-4" /> Unstructured Context (Docs)
                                    </h4>
                                    <div className="text-xs text-muted-foreground max-h-40 overflow-y-auto bg-white dark:bg-black p-2 rounded border">
                                        {result.metadata?.context_used && result.metadata.context_used.length > 0 ? (
                                            <ul className="list-disc list-inside space-y-1">
                                                {result.metadata.context_used.map((doc: string, i: number) => (
                                                    <li key={i}>{doc.substring(0, 150)}...</li>
                                                ))}
                                            </ul>
                                        ) : (
                                            "No documents retrieved."
                                        )}
                                    </div>
                                </div>
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
                            {sampleQuestions.slice(0, 15).map((sample, idx) => (
                                <Button
                                    key={idx}
                                    variant="ghost"
                                    className="justify-start text-left h-auto py-4 px-4 hover:bg-purple-50 hover:border-purple-200 border border-transparent transition-all"
                                    onClick={() => handleSampleClick(sample)}
                                    disabled={streamState.isStreaming}
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
