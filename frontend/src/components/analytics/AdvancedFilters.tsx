"use client";

import { useState } from "react";
import { Search, X, Calendar, MapPin, User, Package, Tag } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import GlassInput from "@/components/GlassInput";
import LiquidButton from "@/components/LiquidButton";
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
            <div className="relative flex flex-col md:flex-row md:items-center gap-3 rounded-[32px] bg-white/[0.03] border border-white/10 px-4 py-3 backdrop-blur-md">
                {/* Search row */}
                <div className="flex items-center gap-2 flex-1 min-w-0">

                    {/* Filter Chips - scrollable on mobile */}
                    <div className="flex items-center gap-2 overflow-x-auto flex-1 min-w-0 scrollbar-hide">
                        {filters.map((filter) => (
                            <Badge
                                key={filter.id}
                                variant="secondary"
                                className="rounded-full bg-white/10 text-white border-white/20 pl-3 pr-2 py-1.5 flex items-center gap-2 shrink-0 backdrop-blur-sm"
                            >
                                {filter.icon}
                                <span className="text-xs font-medium whitespace-nowrap">{filter.label}</span>
                                <button
                                    onClick={() => removeFilter(filter.id)}
                                    className="ml-1 rounded-full hover:bg-white/20 p-0.5 w-5 h-5 flex items-center justify-center transition-colors"
                                >
                                    <X className="h-3 w-3" />
                                </button>
                            </Badge>
                        ))}

                        <div className="flex-1 min-w-[200px]">
                            <GlassInput
                                icon={Search}
                                placeholder="Поиск..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="border-0 bg-transparent shadow-none focus:bg-transparent focus:ring-0 pl-10"
                            />
                        </div>
                    </div>
                </div>

                {/* Quick Filter Buttons - wrap on mobile */}
                <div className="flex items-center justify-center gap-2 flex-wrap sm:flex-nowrap">

                    {/* Date Picker */}
                    <Popover open={showDatePicker} onOpenChange={setShowDatePicker}>
                        <PopoverTrigger asChild>
                            <LiquidButton
                                variant="secondary"
                                icon={Calendar}
                                className="min-w-[100px] h-10 text-xs"
                            >
                                <span className="hidden md:inline">Дата</span>
                            </LiquidButton>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0 bg-[#0A0A0A] border-white/10 text-gray-100">
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
                                <LiquidButton
                                    variant="secondary"
                                    icon={MapPin}
                                    className="min-w-[100px] h-10 text-xs"
                                >
                                    <span className="hidden md:inline">Регион</span>
                                </LiquidButton>
                            </PopoverTrigger>
                            <PopoverContent className="w-48 bg-[#0A0A0A] border-white/10">
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
                                            className="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-white/10 text-gray-300 transition-colors"
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
                                <LiquidButton
                                    variant="secondary"
                                    icon={User}
                                    className="min-w-[100px] h-10 text-xs"
                                >
                                    <span className="hidden md:inline">Агент</span>
                                </LiquidButton>
                            </PopoverTrigger>
                            <PopoverContent className="w-48 bg-[#0A0A0A] border-white/10">
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
                                            className="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-white/10 text-gray-300 transition-colors"
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
