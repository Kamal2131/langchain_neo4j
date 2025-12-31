import { useQuery } from '@tanstack/react-query';
import { TrendingUp, Database, Activity } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { healthApi } from '@/lib/api';

export function AnalyticsPage() {
    const { data: schema, isLoading } = useQuery({
        queryKey: ['schema'],
        queryFn: () => healthApi.getSchema().then(res => res.data),
    });

    const nodeStats = schema?.schema ? Object.entries(schema.schema.node_labels) : [];
    const relStats = schema?.schema ? Object.entries(schema.schema.relationship_types) : [];

    return (
        <div className="container mx-auto p-6 max-w-7xl">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
                    <TrendingUp className="h-8 w-8 text-primary" />
                    Analytics
                </h1>
                <p className="text-muted-foreground">
                    Graph database statistics and insights
                </p>
            </div>

            {/* Connection Status */}
            <Card className="mb-6">
                <CardHeader>
                    <CardTitle>Neo4j Connection</CardTitle>
                    <CardDescription>Database health and status</CardDescription>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <Skeleton className="h-20 w-full" />
                    ) : (
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Status</span>
                                <Badge variant={schema?.neo4j_connected ? 'default' : 'destructive'}>
                                    <Activity className="mr-1 h-3 w-3" />
                                    {schema?.neo4j_connected ? 'Connected' : 'Disconnected'}
                                </Badge>
                            </div>
                            {schema?.neo4j_status && (
                                <div className="flex items-center justify-between">
                                    <span className="text-sm font-medium">Database</span>
                                    <span className="text-sm text-muted-foreground">{schema.neo4j_status}</span>
                                </div>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Graph Stats */}
            <div className="grid gap-4 md:grid-cols-2 mb-6">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Total Nodes</CardTitle>
                        <Database className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {schema?.schema?.total_nodes?.toLocaleString() || 0}
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Total Relationships</CardTitle>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {schema?.schema?.total_relationships?.toLocaleString() || 0}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Node Labels */}
            <Card className="mb-6">
                <CardHeader>
                    <CardTitle>Node Distribution</CardTitle>
                    <CardDescription>Count of nodes by label</CardDescription>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <Skeleton className="h-40 w-full" />
                    ) : (
                        <div className="space-y-2">
                            {nodeStats.map(([label, count]) => (
                                <div key={label} className="flex items-center justify-between py-2 border-b last:border-0">
                                    <span className="font-medium">{label}</span>
                                    <Badge variant="secondary">{count.toLocaleString()}</Badge>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Relationship Types */}
            <Card>
                <CardHeader>
                    <CardTitle>Relationship Distribution</CardTitle>
                    <CardDescription>Count of relationships by type</CardDescription>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <Skeleton className="h-40 w-full" />
                    ) : (
                        <div className="space-y-2">
                            {relStats.map(([type, count]) => (
                                <div key={type} className="flex items-center justify-between py-2 border-b last:border-0">
                                    <span className="font-medium">{type}</span>
                                    <Badge variant="outline">{count.toLocaleString()}</Badge>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
