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
            {/* Mobile-first Search Bar */}
            <div className="relative flex flex-col md:flex-row md:items-center gap-3 rounded-3xl bg-zinc-900/50 border border-zinc-800 px-4 py-3 backdrop-blur-sm">
                {/* Search row */}
                <div className="flex items-center gap-2 flex-1 min-w-0">
                    <Search className="h-5 w-5 text-zinc-400 shrink-0" />

                    {/* Filter Chips - scrollable on mobile */}
                    <div className="flex items-center gap-2 overflow-x-auto flex-1 min-w-0 scrollbar-hide">
                        {filters.map((filter) => (
                            <Badge
                                key={filter.id}
                                variant="secondary"
                                className="rounded-full bg-purple-500/20 text-purple-300 border-purple-500/30 pl-2 pr-1 py-1 flex items-center gap-1 shrink-0"
                            >
                                {filter.icon}
                                <span className="text-xs font-medium whitespace-nowrap">{filter.label}</span>
                                <button
                                    onClick={() => removeFilter(filter.id)}
                                    className="ml-1 rounded-full hover:bg-purple-500/30 p-0.5 min-h-[24px] min-w-[24px] flex items-center justify-center"
                                >
                                    <X className="h-3 w-3" />
                                </button>
                            </Badge>
                        ))}

                        <Input
                            type="text"
                            placeholder="Поиск..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="flex-1 min-w-[120px] border-0 bg-transparent text-sm focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-zinc-500"
                        />
                    </div>
                </div>

                {/* Quick Filter Buttons - wrap on mobile */}
                <div className="flex items-center gap-2 flex-wrap">

                    {/* Date Picker */}
                    <Popover open={showDatePicker} onOpenChange={setShowDatePicker}>
                        <PopoverTrigger asChild>
                            <Button
                                variant="ghost"
                                className="btn-filter"
                            >
                                <Calendar className="h-4 w-4" />
                                <span className="hidden md:inline">Дата</span>
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
                                    className="btn-filter"
                                >
                                    <MapPin className="h-4 w-4" />
                                    <span className="hidden md:inline">Регион</span>
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
                                    className="btn-filter"
                                >
                                    <User className="h-4 w-4" />
                                    <span className="hidden md:inline">Агент</span>
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
