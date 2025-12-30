'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, RefreshCw, Calendar, AlertTriangle } from 'lucide-react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Area,
    AreaChart,
    BarChart,
    Bar,
} from 'recharts';
import { forecastApi } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';

export default function ForecastPage() {
    const [monthsAhead, setMonthsAhead] = useState(3);
    const [forecast, setForecast] = useState<any[]>([]);
    const [seasonality, setSeasonality] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [training, setTraining] = useState(false);

    useEffect(() => {
        loadForecast();
        loadSeasonality();
    }, [monthsAhead]);

    async function loadForecast() {
        setLoading(true);
        try {
            const result = await forecastApi.predict(monthsAhead);
            setForecast(result.forecast);
        } catch (err) {
            // Demo data
            setForecast([
                { date: '2024-07', predicted: 2650000, lower_bound: 2400000, upper_bound: 2900000 },
                { date: '2024-08', predicted: 2800000, lower_bound: 2500000, upper_bound: 3100000 },
                { date: '2024-09', predicted: 2950000, lower_bound: 2600000, upper_bound: 3300000 },
            ]);
        } finally {
            setLoading(false);
        }
    }

    async function loadSeasonality() {
        try {
            const result = await forecastApi.getSeasonality();
            setSeasonality(result);
        } catch (err) {
            setSeasonality({
                monthly: [
                    { month: 'Янв', index: 85 },
                    { month: 'Фев', index: 90 },
                    { month: 'Мар', index: 105 },
                    { month: 'Апр', index: 110 },
                    { month: 'Май', index: 95 },
                    { month: 'Июн', index: 80 },
                    { month: 'Июл', index: 75 },
                    { month: 'Авг', index: 85 },
                    { month: 'Сен', index: 115 },
                    { month: 'Окт', index: 120 },
                    { month: 'Ноя', index: 125 },
                    { month: 'Дек', index: 115 },
                ],
                weekly: [
                    { day: 'Пн', index: 95 },
                    { day: 'Вт', index: 105 },
                    { day: 'Ср', index: 110 },
                    { day: 'Чт', index: 115 },
                    { day: 'Пт', index: 100 },
                    { day: 'Сб', index: 85 },
                    { day: 'Вс', index: 90 },
                ],
            });
        }
    }

    async function trainModel() {
        setTraining(true);
        try {
            await forecastApi.train();
            await loadForecast();
        } catch (err) {
            console.error('Training error:', err);
        } finally {
            setTraining(false);
        }
    }

    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="rounded-lg border bg-background p-3 shadow-lg">
                    <p className="text-sm font-medium">{label}</p>
                    <p className="text-sm text-primary">
                        Прогноз: {formatCurrency(payload[0].value)}
                    </p>
                    {payload[1] && (
                        <p className="text-xs text-muted-foreground">
                            Диапазон: {formatCurrency(payload[1].payload.lower_bound)} - {formatCurrency(payload[1].payload.upper_bound)}
                        </p>
                    )}
                </div>
            );
        }
        return null;
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Прогнозирование продаж</h1>
                    <p className="text-muted-foreground">ML-модель Prophet для предсказания</p>
                </div>
                <div className="flex gap-3">
                    <select
                        value={monthsAhead}
                        onChange={(e) => setMonthsAhead(Number(e.target.value))}
                        className="rounded-lg border border-input bg-background px-4 py-2"
                    >
                        <option value={1}>1 месяц</option>
                        <option value={3}>3 месяца</option>
                        <option value={6}>6 месяцев</option>
                        <option value={12}>12 месяцев</option>
                    </select>
                    <button
                        onClick={trainModel}
                        disabled={training}
                        className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 hover:bg-secondary disabled:opacity-50"
                    >
                        <RefreshCw className={`h-4 w-4 ${training ? 'animate-spin' : ''}`} />
                        {training ? 'Обучение...' : 'Переобучить'}
                    </button>
                </div>
            </div>

            {/* Forecast Chart */}
            <div className="metric-card">
                <div className="mb-4 flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-primary" />
                    <h3 className="font-semibold">Прогноз на {monthsAhead} мес.</h3>
                </div>
                <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={forecast}>
                            <defs>
                                <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                            <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                            <YAxis
                                stroke="hsl(var(--muted-foreground))"
                                fontSize={12}
                                tickFormatter={(v) => `${(v / 1000000).toFixed(1)}M`}
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Area
                                type="monotone"
                                dataKey="predicted"
                                stroke="hsl(var(--primary))"
                                strokeWidth={2}
                                fill="url(#colorForecast)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Seasonality Charts */}
            <div className="grid gap-6 lg:grid-cols-2">
                {/* Monthly Seasonality */}
                <div className="metric-card">
                    <div className="mb-4 flex items-center gap-2">
                        <Calendar className="h-5 w-5 text-green-500" />
                        <h3 className="font-semibold">Сезонность по месяцам</h3>
                    </div>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={seasonality?.monthly || []}>
                                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                                <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} domain={[60, 140]} />
                                <Tooltip />
                                <Bar
                                    dataKey="index"
                                    fill="hsl(142, 76%, 36%)"
                                    radius={[4, 4, 0, 0]}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <p className="mt-2 text-xs text-muted-foreground text-center">
                        100 = базовый уровень. Выше 100 — сезонный рост.
                    </p>
                </div>

                {/* Weekly Seasonality */}
                <div className="metric-card">
                    <div className="mb-4 flex items-center gap-2">
                        <Calendar className="h-5 w-5 text-purple-500" />
                        <h3 className="font-semibold">Сезонность по дням недели</h3>
                    </div>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={seasonality?.weekly || []}>
                                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                                <XAxis dataKey="day" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} domain={[60, 140]} />
                                <Tooltip />
                                <Bar
                                    dataKey="index"
                                    fill="hsl(262, 83%, 58%)"
                                    radius={[4, 4, 0, 0]}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}
