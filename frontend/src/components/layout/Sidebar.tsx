import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import {
    Database,
    Users,
    FolderKanban,
    TrendingUp,
    MessageSquare,
    Building2,
    ChevronRight,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const navigation = [
    {
        name: 'AI Query',
        href: '/',
        icon: MessageSquare,
        description: 'Natural language search',
        badge: 'AI'
    },
    {
        name: 'Employees',
        href: '/employees',
        icon: Users,
        description: '100 team members'
    },
    {
        name: 'Projects',
        href: '/projects',
        icon: FolderKanban,
        description: '50 active projects'
    },
    {
        name: 'Departments',
        href: '/departments',
        icon: Building2,
        description: '8 departments'
    },
    {
        name: 'Analytics',
        href: '/analytics',
        icon: TrendingUp,
        description: 'Graph insights'
    },
];

export function Sidebar() {
    const location = useLocation();

    return (
        <div className="flex h-full w-72 flex-col border-r bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900">
            {/* Header */}
            <div className="flex h-16 items-center gap-3 border-b px-6 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg">
                    <Database className="h-5 w-5 text-white" />
                </div>
                <div>
                    <h1 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        Neo4j KB
                    </h1>
                    <p className="text-xs text-muted-foreground">Knowledge Base</p>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-1 p-4">
                {navigation.map((item) => {
                    const isActive = location.pathname === item.href;
                    return (
                        <Link
                            key={item.name}
                            to={item.href}
                            className={cn(
                                'group relative flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200',
                                isActive
                                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/25'
                                    : 'text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
                            )}
                        >
                            <item.icon className={cn(
                                "h-5 w-5 transition-transform group-hover:scale-110",
                                isActive ? "text-white" : "text-slate-500"
                            )} />
                            <div className="flex-1">
                                <div className="flex items-center gap-2">
                                    {item.name}
                                    {item.badge && (
                                        <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                                            {item.badge}
                                        </Badge>
                                    )}
                                </div>
                                <p className={cn(
                                    "text-xs mt-0.5",
                                    isActive ? "text-blue-100" : "text-slate-500"
                                )}>
                                    {item.description}
                                </p>
                            </div>
                            {isActive && (
                                <ChevronRight className="h-4 w-4" />
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer Stats */}
            <div className="border-t p-4 space-y-3 bg-slate-50/50 dark:bg-slate-900/50">
                <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-white dark:bg-slate-800 rounded-lg p-2.5 shadow-sm">
                        <p className="text-muted-foreground">Nodes</p>
                        <p className="text-lg font-bold">359</p>
                    </div>
                    <div className="bg-white dark:bg-slate-800 rounded-lg p-2.5 shadow-sm">
                        <p className="text-muted-foreground">Relations</p>
                        <p className="text-lg font-bold">1.4K</p>
                    </div>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                    <span>Connected · v1.0.0</span>
                </div>
            </div>
        </div>
    );
}
