import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FolderKanban, DollarSign, Users as UsersIcon, AlertCircle, Filter, Clock } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { companyApi } from '@/lib/api';
import type { Project } from '@/types/api';

const STATUS_COLORS: Record<Project['status'], string> = {
    active: 'bg-emerald-500',
    completed: 'bg-blue-500',
    planning: 'bg-amber-500',
    'on-hold': 'bg-orange-500',
    cancelled: 'bg-red-500',
};

const STATUS_TEXT_COLORS: Record<Project['status'], string> = {
    active: 'text-emerald-700 bg-emerald-50 border-emerald-200',
    completed: 'text-blue-700 bg-blue-50 border-blue-200',
    planning: 'text-amber-700 bg-amber-50 border-amber-200',
    'on-hold': 'text-orange-700 bg-orange-50 border-orange-200',
    cancelled: 'text-red-700 bg-red-50 border-red-200',
};

export function ProjectsPage() {
    const [status, setStatus] = useState<string>('all');

    const { data: projects, isLoading } = useQuery({
        queryKey: ['projects', status === 'all' ? undefined : status],
        queryFn: () => companyApi.getProjects(status === 'all' ? undefined : status).then(res => res.data),
    });

    const stats = {
        total: projects?.length || 0,
        active: projects?.filter(p => p.status === 'active').length || 0,
        totalBudget: projects?.reduce((sum, p) => sum + (p.budget || 0), 0) || 0,
    };

    return (
        <div className="container mx-auto p-8 max-w-7xl space-y-8">
            {/* Header */}
            <div className="space-y-3">
                <div className="flex items-center gap-3">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg">
                        <FolderKanban className="h-6 w-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                            Projects Dashboard
                        </h1>
                        <p className="text-muted-foreground mt-1">
                            Manage and track all company projects
                        </p>
                    </div>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid gap-6 md:grid-cols-3">
                <Card className="border-2 hover:shadow-lg transition-shadow bg-gradient-to-br from-white to-indigo-50">
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
                        <FolderKanban className="h-5 w-5 text-indigo-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-4xl font-bold text-indigo-600">{stats.total}</div>
                        <p className="text-xs text-muted-foreground mt-1">Across all departments</p>
                    </CardContent>
                </Card>
                <Card className="border-2 hover:shadow-lg transition-shadow bg-gradient-to-br from-white to-emerald-50">
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Active Projects</CardTitle>
                        <AlertCircle className="h-5 w-5 text-emerald-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-4xl font-bold text-emerald-600">{stats.active}</div>
                        <p className="text-xs text-muted-foreground mt-1">In development</p>
                    </CardContent>
                </Card>
                <Card className="border-2 hover:shadow-lg transition-shadow bg-gradient-to-br from-white to-purple-50">
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Total Budget</CardTitle>
                        <DollarSign className="h-5 w-5 text-purple-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-4xl font-bold text-purple-600">
                            ${(stats.totalBudget / 1_000_000).toFixed(1)}M
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">Combined investment</p>
                    </CardContent>
                </Card>
            </div>

            {/* Filter */}
            <Card className="border-2 shadow-lg">
                <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                        <Filter className="h-5 w-5 text-muted-foreground" />
                        <Select value={status} onValueChange={setStatus}>
                            <SelectTrigger className="w-[240px] h-11">
                                <SelectValue placeholder="Filter by status" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Projects</SelectItem>
                                <SelectItem value="active">Active</SelectItem>
                                <SelectItem value="completed">Completed</SelectItem>
                                <SelectItem value="planning">Planning</SelectItem>
                                <SelectItem value="on-hold">On Hold</SelectItem>
                                <SelectItem value="cancelled">Cancelled</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </CardContent>
            </Card>

            {/* Projects Grid */}
            {isLoading ? (
                <div className="grid gap-6 md:grid-cols-2">
                    {[...Array(4)].map((_, i) => (
                        <Card key={i}>
                            <CardHeader>
                                <Skeleton className="h-4 w-3/4 mb-2" />
                                <Skeleton className="h-3 w-1/2" />
                            </CardHeader>
                            <CardContent>
                                <Skeleton className="h-20 w-full" />
                            </CardContent>
                        </Card>
                    ))}
                </div>
            ) : (
                <div className="grid gap-6 md:grid-cols-2">
                    {projects?.map((project) => (
                        <Card
                            key={project.project_id}
                            className="group hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 border-2 hover:border-indigo-200"
                        >
                            <CardHeader className="bg-gradient-to-r from-indigo-50/50 to-purple-50/50">
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1 min-w-0">
                                        <CardTitle className="text-lg group-hover:text-indigo-600 transition-colors truncate">
                                            {project.name}
                                        </CardTitle>
                                        <CardDescription className="mt-2 flex items-center gap-1.5">
                                            <Clock className="h-3.5 w-3.5" />
                                            {project.type}
                                        </CardDescription>
                                    </div>
                                    <div className="flex flex-col items-end gap-2 shrink-0">
                                        <Badge className={`border ${STATUS_TEXT_COLORS[project.status]}`}>
                                            <div className={`w-2 h-2 rounded-full ${STATUS_COLORS[project.status]} mr-1.5`} />
                                            {project.status}
                                        </Badge>
                                        {project.priority && (
                                            <Badge
                                                variant="outline"
                                                className={`text-xs ${project.priority === 'High'
                                                        ? 'border-red-300 text-red-700'
                                                        : project.priority === 'Medium'
                                                            ? 'border-yellow-300 text-yellow-700'
                                                            : 'border-blue-300 text-blue-700'
                                                    }`}
                                            >
                                                {project.priority} Priority
                                            </Badge>
                                        )}
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent className="pt-4 space-y-4">
                                <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">
                                    {project.description}
                                </p>
                                <div className="flex items-center justify-between pt-3 border-t">
                                    <div className="flex items-center gap-2 text-sm">
                                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100">
                                            <UsersIcon className="h-4 w-4 text-indigo-600" />
                                        </div>
                                        <div>
                                            <p className="font-semibold">{project.team_size}</p>
                                            <p className="text-xs text-muted-foreground">Members</p>
                                        </div>
                                    </div>
                                    {project.budget && (
                                        <div className="flex items-center gap-2 text-sm">
                                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-100">
                                                <DollarSign className="h-4 w-4 text-purple-600" />
                                            </div>
                                            <div>
                                                <p className="font-semibold">${(project.budget / 1000).toFixed(0)}K</p>
                                                <p className="text-xs text-muted-foreground">Budget</p>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}

            {projects?.length === 0 && !isLoading && (
                <Card className="shadow-lg">
                    <CardContent className="py-16 text-center">
                        <FolderKanban className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                        <p className="text-lg font-medium text-muted-foreground">No projects found</p>
                        <p className="text-sm text-muted-foreground mt-1">Try adjusting your filters</p>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
