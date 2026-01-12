"use client";

import { useState } from "react";
import { Search, X, Calendar, MapPin, User, Package, Tag } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import { Calendar as CalendarComponent } from "@/components/ui/calendar";
import { format } from "date-fns";

export interface FilterChip {
    id: string;
    type: "date" | "region" | "agent" | "product" | "category";
    label: string;
    value: string;
    icon: React.ReactNode;
}

interface AdvancedFiltersProps {
    onFiltersChange?: (filters: FilterChip[]) => void;
    availableRegions?: string[];
    availableCategories?: string[];
    availableAgents?: Array<{ id: string; name: string }>;
}

export function AdvancedFilters({
    onFiltersChange,
    availableRegions = [],
    availableCategories = [],
    availableAgents = [],
}: AdvancedFiltersProps) {
    const [filters, setFilters] = useState<FilterChip[]>([]);
    const [searchQuery, setSearchQuery] = useState("");
    const [showDatePicker, setShowDatePicker] = useState(false);

    const removeFilter = (id: string) => {
        const newFilters = filters.filter((f) => f.id !== id);
        setFilters(newFilters);
        onFiltersChange?.(newFilters);
    };

    const addFilter = (filter: Omit<FilterChip, "id">) => {
        const newFilter: FilterChip = {
            ...filter,
            id: `${filter.type}-${Date.now()}`,
        };
        const newFilters = [...filters, newFilter];
        setFilters(newFilters);
        onFiltersChange?.(newFilters);
    };

    const handleDateSelect = (date: Date | undefined) => {
        if (date) {
            addFilter({
                type: "date",
                label: format(date, "MMM yyyy"),
                value: date.toISOString(),
                icon: <Calendar className="h-3 w-3" />,
            });
            setShowDatePicker(false);
        }
    };

    const getIconForType = (type: FilterChip["type"]) => {
        switch (type) {
            case "date":
                return <Calendar className="h-3 w-3" />;
            case "region":
                return <MapPin className="h-3 w-3" />;
            case "agent":
                return <User className="h-3 w-3" />;
            case "product":
                return <Package className="h-3 w-3" />;
            case "category":
                return <Tag className="h-3 w-3" />;
        }
    };

    return (
        <div className="w-full">
            {/* Pill-shaped Search Bar */}
            <div className="relative flex items-center gap-2 rounded-full bg-zinc-900/50 border border-zinc-800 px-4 py-3 backdrop-blur-sm">
                <Search className="h-5 w-5 text-zinc-400" />

                {/* Filter Chips */}
                <div className="flex flex-wrap items-center gap-2 flex-1">
                    {filters.map((filter) => (
                        <Badge
                            key={filter.id}
                            variant="secondary"
                            className="rounded-full bg-purple-500/20 text-purple-300 border-purple-500/30 pl-2 pr-1 py-1 flex items-center gap-1"
                        >
                            {filter.icon}
                            <span className="text-xs font-medium">{filter.label}</span>
                            <button
                                onClick={() => removeFilter(filter.id)}
                                className="ml-1 rounded-full hover:bg-purple-500/30 p-0.5"
                            >
                                <X className="h-3 w-3" />
                            </button>
                        </Badge>
                    ))}

                    <Input
                        type="text"
                        placeholder="Search for insights, metrics, or reports..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="flex-1 border-0 bg-transparent text-sm focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-zinc-500"
                    />
                </div>

                {/* Quick Filter Buttons */}
                <div className="flex items-center gap-2">
                    {/* Date Picker */}
                    <Popover open={showDatePicker} onOpenChange={setShowDatePicker}>
                        <PopoverTrigger asChild>
                            <Button
                                variant="ghost"
                                size="sm"
                                className="rounded-full h-8 px-3 text-xs bg-cyan-500/10 text-cyan-300 hover:bg-cyan-500/20 border border-cyan-500/30"
                            >
                                <Calendar className="h-3 w-3 mr-1" />
                                Date
                            </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0 bg-zinc-900 border-zinc-800">
                            <CalendarComponent
                                mode="single"
                                onSelect={handleDateSelect}
                                className="rounded-md"
                            />
                        </PopoverContent>
                    </Popover>

                    {/* Region Filter */}
                    {availableRegions.length > 0 && (
                        <Popover>
                            <PopoverTrigger asChild>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    className="rounded-full h-8 px-3 text-xs bg-cyan-500/10 text-cyan-300 hover:bg-cyan-500/20 border border-cyan-500/30"
                                >
                                    <MapPin className="h-3 w-3 mr-1" />
                                    Region
                                </Button>
                            </PopoverTrigger>
                            <PopoverContent className="w-48 bg-zinc-900 border-zinc-800">
                                <div className="space-y-1">
                                    {availableRegions.map((region) => (
                                        <button
                                            key={region}
                                            onClick={() => {
                                                addFilter({
                                                    type: "region",
                                                    label: region,
                                                    value: region,
                                                    icon: <MapPin className="h-3 w-3" />,
                                                });
                                            }}
                                            className="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-zinc-800 text-zinc-300"
                                        >
                                            {region}
                                        </button>
                                    ))}
                                </div>
                            </PopoverContent>
                        </Popover>
                    )}

                    {/* Agent Filter */}
                    {availableAgents.length > 0 && (
                        <Popover>
                            <PopoverTrigger asChild>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    className="rounded-full h-8 px-3 text-xs bg-cyan-500/10 text-cyan-300 hover:bg-cyan-500/20 border border-cyan-500/30"
                                >
                                    <User className="h-3 w-3 mr-1" />
                                    Agent
                                </Button>
                            </PopoverTrigger>
                            <PopoverContent className="w-48 bg-zinc-900 border-zinc-800">
                                <div className="space-y-1">
                                    {availableAgents.map((agent) => (
                                        <button
                                            key={agent.id}
                                            onClick={() => {
                                                addFilter({
                                                    type: "agent",
                                                    label: agent.name,
                                                    value: agent.id,
                                                    icon: <User className="h-3 w-3" />,
                                                });
                                            }}
                                            className="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-zinc-800 text-zinc-300"
                                        >
                                            {agent.name}
                                        </button>
                                    ))}
                                </div>
                            </PopoverContent>
                        </Popover>
                    )}
                </div>
            </div>
        </div>
    );
}
