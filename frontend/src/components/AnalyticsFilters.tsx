'use client';

import { useState, useEffect } from 'react';
import { Filter, Calendar } from 'lucide-react';
import { extAnalyticsApi } from '@/lib/api';

interface FiltersProps {
    onFilterChange: (filters: { year?: number; month?: number }) => void;
    defaultYear?: number;
    defaultMonth?: number;
}

export function AnalyticsFilters({ onFilterChange, defaultYear, defaultMonth }: FiltersProps) {
    const currentYear = new Date().getFullYear();
    const [availableYears, setAvailableYears] = useState<number[]>([currentYear]);
    const [selectedYear, setSelectedYear] = useState<number | undefined>(defaultYear);
    const [selectedMonth, setSelectedMonth] = useState<number | undefined>(defaultMonth);

    const months = [
        { value: undefined, label: 'Все месяцы' },
        { value: 1, label: 'Январь' },
        { value: 2, label: 'Февраль' },
        { value: 3, label: 'Март' },
        { value: 4, label: 'Апрель' },
        { value: 5, label: 'Май' },
        { value: 6, label: 'Июнь' },
        { value: 7, label: 'Июль' },
        { value: 8, label: 'Август' },
        { value: 9, label: 'Сентябрь' },
        { value: 10, label: 'Октябрь' },
        { value: 11, label: 'Ноябрь' },
        { value: 12, label: 'Декабрь' },
    ];

    useEffect(() => {
        loadYears();
    }, []);

    async function loadYears() {
        try {
            const result = await extAnalyticsApi.getAvailableYears();
            if (result.years.length > 0) {
                setAvailableYears(result.years);
            }
        } catch (err) {
            console.error('Failed to load years:', err);
        }
    }

    const handleYearChange = (year: string) => {
        const newYear = year === 'all' ? undefined : parseInt(year);
        setSelectedYear(newYear);
        onFilterChange({ year: newYear, month: selectedMonth });
    };

    const handleMonthChange = (month: string) => {
        const newMonth = month === 'all' ? undefined : parseInt(month);
        setSelectedMonth(newMonth);
        onFilterChange({ year: selectedYear, month: newMonth });
    };

    return (
        <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 text-[#808080]">
                <Filter className="h-4 w-4" />
                <span className="text-sm hidden sm:inline">Фильтры:</span>
            </div>

            {/* Year Filter */}
            <select
                value={selectedYear ?? 'all'}
                onChange={(e) => handleYearChange(e.target.value)}
                className="rounded-[4px] bg-[#111] border border-[#333333] px-3 py-2 text-sm text-white focus:outline-none focus:border-[#404040] transition-colors cursor-pointer min-w-[100px]"
            >
                <option value="all">Все годы</option>
                {availableYears.map((year) => (
                    <option key={year} value={year}>{year}</option>
                ))}
            </select>

            {/* Month Filter */}
            <select
                value={selectedMonth ?? 'all'}
                onChange={(e) => handleMonthChange(e.target.value)}
                className="rounded-[4px] bg-[#111] border border-[#333333] px-3 py-2 text-sm text-white focus:outline-none focus:border-[#404040] transition-colors cursor-pointer min-w-[130px]"
            >
                {months.map((month) => (
                    <option key={month.label} value={month.value ?? 'all'}>
                        {month.label}
                    </option>
                ))}
            </select>
        </div>
    );
}
