import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area
} from 'recharts';
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Sparkles, TrendingUp } from "lucide-react";

export interface ChartData {
    type: 'bar' | 'area' | 'line';
    title: string;
    data: any[];
    xKey: string;
    dataKey: string;
    color?: string;
}

export interface MessageContent {
    text: string;
    chart?: ChartData;
    table?: {
        headers: string[];
        rows: string[][];
    };
}

interface GenerativeMessageProps {
    content: MessageContent;
    role: 'user' | 'assistant';
}

export default function GenerativeMessage({ content, role }: GenerativeMessageProps) {
    const isUser = role === 'user';

    return (
        <div className={cn(
            "flex w-full",
            isUser ? "justify-end" : "justify-start"
        )}>
            <div className={cn(
                "max-w-[85%] lg:max-w-[75%] space-y-4",
                isUser ? "ml-auto" : "mr-auto"
            )}>
                {/* Text Bubble */}
                <div className={cn(
                    "p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap animate-in fade-in duration-300",
                    isUser
                        ? "bg-rose-600 text-white rounded-tr-sm"
                        : "bg-[#2A2A2A] text-gray-200 rounded-tl-sm border border-[#333333] shadow-sm"
                )}>
                    {content.text}
                </div>

                {/* Generative Artifacts (Charts/Tables) - Only for Assistant */}
                {!isUser && content.chart && (
                    <div className="animate-in zoom-in-95 duration-500 delay-150">
                        <Card className="bg-[#1E1E1E] border-[#333333] p-4 sm:p-6 overflow-hidden">
                            <div className="flex items-center gap-2 mb-6">
                                <div className="p-1.5 rounded-md bg-rose-500/10">
                                    <TrendingUp className="w-4 h-4 text-rose-500" />
                                </div>
                                <h3 className="font-medium text-gray-200 text-sm tracking-wide">
                                    {content.chart.title}
                                </h3>
                            </div>

                            <div className="h-[200px] sm:h-[250px] w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    {content.chart.type === 'area' ? (
                                        <AreaChart data={content.chart.data}>
                                            <defs>
                                                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor={content.chart.color || "#e11d48"} stopOpacity={0.3} />
                                                    <stop offset="95%" stopColor={content.chart.color || "#e11d48"} stopOpacity={0} />
                                                </linearGradient>
                                            </defs>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#333333" vertical={false} />
                                            <XAxis
                                                dataKey={content.chart.xKey}
                                                stroke="#666666"
                                                fontSize={12}
                                                tickLine={false}
                                                axisLine={false}
                                                dy={10}
                                            />
                                            <YAxis
                                                stroke="#666666"
                                                fontSize={12}
                                                tickLine={false}
                                                axisLine={false}
                                                tickFormatter={(value) => `${value}`}
                                                dx={-10}
                                            />
                                            <Tooltip
                                                contentStyle={{ backgroundColor: '#262626', border: '1px solid #404040', borderRadius: '8px', color: '#fff' }}
                                                itemStyle={{ color: '#fff' }}
                                            />
                                            <Area
                                                type="monotone"
                                                dataKey={content.chart.dataKey}
                                                stroke={content.chart.color || "#e11d48"}
                                                fillOpacity={1}
                                                fill="url(#colorValue)"
                                            />
                                        </AreaChart>
                                    ) : (
                                        <BarChart data={content.chart.data}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#333333" vertical={false} />
                                            <XAxis
                                                dataKey={content.chart.xKey}
                                                stroke="#666666"
                                                fontSize={12}
                                                tickLine={false}
                                                axisLine={false}
                                                dy={10}
                                            />
                                            <YAxis
                                                stroke="#666666"
                                                fontSize={12}
                                                tickLine={false}
                                                axisLine={false}
                                                dx={-10}
                                            />
                                            <Tooltip
                                                cursor={{ fill: '#333333', opacity: 0.4 }}
                                                contentStyle={{ backgroundColor: '#262626', border: '1px solid #404040', borderRadius: '8px', color: '#fff' }}
                                            />
                                            <Bar
                                                dataKey={content.chart.dataKey}
                                                fill={content.chart.color || "#e11d48"}
                                                radius={[4, 4, 0, 0]}
                                                barSize={40}
                                            />
                                        </BarChart>
                                    )}
                                </ResponsiveContainer>
                            </div>
                        </Card>
                    </div>
                )}
            </div>
        </div>
    );
}
