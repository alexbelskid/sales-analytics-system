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
import { Sparkles, TrendingUp, Table as TableIcon } from "lucide-react";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from "@/components/ui/table";

export interface ChartData {
    type: 'bar' | 'area' | 'line';
    title: string;
    data: any[];
    xKey: string;
    dataKey: string;
    color?: string;
}

export interface TableData {
    title?: string;
    headers: string[];
    rows: (string | number)[][];
}

export interface MessageContent {
    text: string;
    chart?: ChartData;
    table?: TableData;
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
                "max-w-[85%] lg:max-w-[90%] space-y-4",
                isUser ? "ml-auto" : "mr-auto"
            )}>
                {/* Text Bubble */}
                <div className={cn(
                    "p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap animate-in fade-in duration-300",
                    isUser
                        ? "bg-rose-600 text-white rounded-tr-sm shadow-md shadow-rose-900/10"
                        : "bg-[#2A2A2A] text-gray-200 rounded-tl-sm border border-[#333333] shadow-sm"
                )}>
                    {(() => {
                        // Very simple parser for <thought> tag
                        const thoughtMatch = content.text.match(/<thought>([\s\S]*?)<\/thought>/);
                        if (thoughtMatch && !isUser) {
                            const thoughtContent = thoughtMatch[1].trim();
                            const mainContent = content.text.replace(/<thought>[\s\S]*?<\/thought>/, "").trim();

                            return (
                                <div className="space-y-3">
                                    <div className="group">
                                        <details className="text-xs">
                                            <summary className="cursor-pointer list-none font-medium text-[#808080] hover:text-rose-400 flex items-center gap-2 transition-colors select-none">
                                                <Sparkles className="w-3 h-3" />
                                                Thinking Process
                                                <div className="group-open:rotate-180 transition-transform duration-200">
                                                    <svg width="10" height="6" viewBox="0 0 10 6" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                        <path d="M1 1L5 5L9 1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                                    </svg>
                                                </div>
                                            </summary>
                                            <div className="mt-2 pl-3 border-l-2 border-[#404040] text-gray-400 italic">
                                                {thoughtContent}
                                            </div>
                                        </details>
                                    </div>
                                    <div className="pt-1">
                                        {mainContent}
                                    </div>
                                </div>
                            );
                        }
                        return content.text;
                    })()}
                </div>

                {/* Generative Artifacts (Charts/Tables) - Only for Assistant */}
                {!isUser && content.chart && (
                    <div className="animate-in zoom-in-95 duration-500 delay-150">
                        <Card className="bg-[#1E1E1E] border-[#333333] p-4 sm:p-6 overflow-hidden shadow-lg shadow-black/20">
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

                {!isUser && content.table && (
                    <div className="animate-in zoom-in-95 duration-500 delay-200">
                        <Card className="bg-[#1E1E1E] border-[#333333] overflow-hidden shadow-lg shadow-black/20">
                            {content.table.title && (
                                <div className="px-4 py-3 border-b border-[#333333] flex items-center gap-2 bg-[#262626]/50">
                                    <TableIcon className="w-4 h-4 text-rose-500" />
                                    <h3 className="font-medium text-gray-200 text-xs uppercase tracking-wider">
                                        {content.table.title}
                                    </h3>
                                </div>
                            )}
                            <div className="max-h-[300px] overflow-auto">
                                <Table>
                                    <TableHeader>
                                        <TableRow className="border-[#333333] hover:bg-transparent">
                                            {content.table.headers.map((header, i) => (
                                                <TableHead key={i} className="text-[#808080] font-medium text-xs h-9">
                                                    {header}
                                                </TableHead>
                                            ))}
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {content.table.rows.map((row, i) => (
                                            <TableRow key={i} className="border-[#333333] hover:bg-[#262626]">
                                                {row.map((cell, j) => (
                                                    <TableCell key={j} className="text-gray-300 py-2 text-xs">
                                                        {cell}
                                                    </TableCell>
                                                ))}
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </div>
                        </Card>
                    </div>
                )}
            </div>
        </div>
    );
}
