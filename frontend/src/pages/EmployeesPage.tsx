import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Users, Search, Building2, Mail, Briefcase, Star } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { companyApi } from '@/lib/api';

export function EmployeesPage() {
    const [search, setSearch] = useState('');
    const [department, setDepartment] = useState<string>('all');

    const { data: employees, isLoading } = useQuery({
        queryKey: ['employees', department === 'all' ? undefined : department],
        queryFn: () => companyApi.getEmployees(department === 'all' ? undefined : department).then(res => res.data),
    });

    const filtered = employees?.filter(emp =>
        emp.name.toLowerCase().includes(search.toLowerCase()) ||
        emp.email.toLowerCase().includes(search.toLowerCase()) ||
        emp.title.toLowerCase().includes(search.toLowerCase())
    );

    const departments = [...new Set(employees?.map(e => e.department) || [])];

    return (
        <div className="container mx-auto p-8 max-w-7xl space-y-8">
            {/* Header */}
            <div className="space-y-3">
                <div className="flex items-center gap-3">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 shadow-lg">
                        <Users className="h-6 w-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                            Employee Directory
                        </h1>
                        <p className="text-muted-foreground mt-1">
                            Browse and search through {employees?.length || 0} team members
                        </p>
                    </div>
                </div>
            </div>

            {/* Filters */}
            <Card className="border-2 shadow-lg">
                <CardContent className="pt-6">
                    <div className="flex gap-4">
                        <div className="flex-1 relative">
                            <Search className="absolute left-3 top-3.5 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder="Search by name, email, or title..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="pl-10 h-12 text-base"
                            />
                        </div>
                        <Select value={department} onValueChange={setDepartment}>
                            <SelectTrigger className="w-[220px] h-12">
                                <SelectValue placeholder="All Departments" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Departments</SelectItem>
                                {departments.map(dept => (
                                    <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                </CardContent>
            </Card>

            {/* Stats Bar */}
            <div className="grid gap-4 md:grid-cols-3">
                <Card className="border-l-4 border-l-blue-500">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Total Employees</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{filtered?.length || 0}</div>
                    </CardContent>
                </Card>
                <Card className="border-l-4 border-l-purple-500">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Departments</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{departments.length}</div>
                    </CardContent>
                </Card>
                <Card className="border-l-4 border-l-green-500">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Unique Skills</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">
                            {new Set(employees?.flatMap(e => e.skills) || []).size}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Employee Grid */}
            {isLoading ? (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {[...Array(6)].map((_, i) => (
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
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {filtered?.map((employee) => (
                        <Card
                            key={employee.email}
                            className="group hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 border-2 hover:border-blue-200"
                        >
                            <CardHeader className="bg-gradient-to-r from-blue-50/50 to-cyan-50/50">
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <CardTitle className="text-lg group-hover:text-blue-600 transition-colors">
                                            {employee.name}
                                        </CardTitle>
                                        <CardDescription className="flex items-center gap-1.5 mt-2">
                                            <Briefcase className="h-3.5 w-3.5" />
                                            {employee.title}
                                        </CardDescription>
                                    </div>
                                    {employee.skills.length > 5 && (
                                        <Star className="h-5 w-5 text-yellow-500" />
                                    )}
                                </div>
                            </CardHeader>
                            <CardContent className="pt-4 space-y-3">
                                <div className="flex items-center gap-2 text-sm">
                                    <Building2 className="h-4 w-4 text-blue-600" />
                                    <span className="font-medium">{employee.department}</span>
                                </div>
                                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <Mail className="h-4 w-4" />
                                    <span className="truncate">{employee.email}</span>
                                </div>
                                {employee.skills.length > 0 && (
                                    <div className="pt-2">
                                        <p className="text-xs text-muted-foreground mb-2">Skills</p>
                                        <div className="flex flex-wrap gap-1.5">
                                            {employee.skills.slice(0, 5).map((skill) => (
                                                <Badge
                                                    key={skill}
                                                    variant="secondary"
                                                    className="text-xs bg-blue-50 text-blue-700 border-blue-200"
                                                >
                                                    {skill}
                                                </Badge>
                                            ))}
                                            {employee.skills.length > 5 && (
                                                <Badge variant="outline" className="text-xs">
                                                    +{employee.skills.length - 5} more
                                                </Badge>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}

            {filtered?.length === 0 && !isLoading && (
                <Card className="shadow-lg">
                    <CardContent className="py-16 text-center">
                        <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                        <p className="text-lg font-medium text-muted-foreground">No employees found</p>
                        <p className="text-sm text-muted-foreground mt-1">Try adjusting your search or filters</p>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
