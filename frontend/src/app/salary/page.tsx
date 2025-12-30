'use client';

import { useState, useEffect } from 'react';
import { Calculator, Download, Users } from 'lucide-react';
import { salaryApi } from '@/lib/api';
import { formatCurrency, downloadBlob, monthNames } from '@/lib/utils';

interface SalaryData {
    agent_id: string;
    agent_name: string;
    base_salary: number;
    sales_amount: number;
    commission_rate: number;
    commission: number;
    bonus: number;
    penalty: number;
    total_salary: number;
}

export default function SalaryPage() {
    const currentDate = new Date();
    const [year, setYear] = useState(currentDate.getFullYear());
    const [month, setMonth] = useState(currentDate.getMonth() + 1);
    const [salaries, setSalaries] = useState<SalaryData[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadSalaries();
    }, [year, month]);

    async function loadSalaries() {
        setLoading(true);
        try {
            const data = await salaryApi.calculate(year, month);
            setSalaries(data);
        } catch (err) {
            // Demo data
            setSalaries([
                {
                    agent_id: '1',
                    agent_name: 'Иванов Иван',
                    base_salary: 50000,
                    sales_amount: 850000,
                    commission_rate: 5,
                    commission: 42500,
                    bonus: 5000,
                    penalty: 0,
                    total_salary: 97500,
                },
                {
                    agent_id: '2',
                    agent_name: 'Петрова Мария',
                    base_salary: 45000,
                    sales_amount: 620000,
                    commission_rate: 5,
                    commission: 31000,
                    bonus: 0,
                    penalty: 0,
                    total_salary: 76000,
                },
                {
                    agent_id: '3',
                    agent_name: 'Сидоров Алексей',
                    base_salary: 50000,
                    sales_amount: 1200000,
                    commission_rate: 6,
                    commission: 72000,
                    bonus: 10000,
                    penalty: 0,
                    total_salary: 132000,
                },
            ]);
        } finally {
            setLoading(false);
        }
    }

    async function exportExcel() {
        try {
            const blob = await salaryApi.exportExcel(year, month);
            downloadBlob(blob, `salary_${year}_${month}.xlsx`);
        } catch (err) {
            console.error('Export error:', err);
        }
    }

    const totalSalary = salaries.reduce((sum, s) => sum + s.total_salary, 0);
    const totalSales = salaries.reduce((sum, s) => sum + s.sales_amount, 0);

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Расчёт зарплат</h1>
                    <p className="text-muted-foreground">
                        Оклад + % от продаж + бонусы - штрафы
                    </p>
                </div>
                <div className="flex gap-3">
                    <select
                        value={month}
                        onChange={(e) => setMonth(Number(e.target.value))}
                        className="rounded-lg border border-input bg-background px-4 py-2"
                    >
                        {monthNames.map((name, i) => (
                            <option key={i} value={i + 1}>
                                {name}
                            </option>
                        ))}
                    </select>
                    <select
                        value={year}
                        onChange={(e) => setYear(Number(e.target.value))}
                        className="rounded-lg border border-input bg-background px-4 py-2"
                    >
                        {[2023, 2024, 2025].map((y) => (
                            <option key={y} value={y}>
                                {y}
                            </option>
                        ))}
                    </select>
                    <button
                        onClick={exportExcel}
                        className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 font-medium text-white hover:bg-primary/90"
                    >
                        <Download className="h-4 w-4" />
                        Экспорт Excel
                    </button>
                </div>
            </div>

            {/* Summary Cards */}
            <div className="grid gap-4 md:grid-cols-3">
                <div className="metric-card">
                    <div className="flex items-center gap-2 text-muted-foreground">
                        <Users className="h-5 w-5" />
                        <span>Агентов</span>
                    </div>
                    <p className="mt-2 text-3xl font-bold">{salaries.length}</p>
                </div>
                <div className="metric-card">
                    <div className="flex items-center gap-2 text-muted-foreground">
                        <Calculator className="h-5 w-5" />
                        <span>Общий ФОТ</span>
                    </div>
                    <p className="mt-2 text-3xl font-bold">{formatCurrency(totalSalary)}</p>
                </div>
                <div className="metric-card">
                    <div className="flex items-center gap-2 text-muted-foreground">
                        <Calculator className="h-5 w-5" />
                        <span>Общие продажи</span>
                    </div>
                    <p className="mt-2 text-3xl font-bold">{formatCurrency(totalSales)}</p>
                </div>
            </div>

            {/* Salary Table */}
            <div className="metric-card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Агент</th>
                                <th className="px-4 py-3 text-right font-medium text-muted-foreground">Оклад</th>
                                <th className="px-4 py-3 text-right font-medium text-muted-foreground">Продажи</th>
                                <th className="px-4 py-3 text-right font-medium text-muted-foreground">%</th>
                                <th className="px-4 py-3 text-right font-medium text-muted-foreground">Комиссия</th>
                                <th className="px-4 py-3 text-right font-medium text-muted-foreground">Бонус</th>
                                <th className="px-4 py-3 text-right font-medium text-muted-foreground">Штраф</th>
                                <th className="px-4 py-3 text-right font-medium">ИТОГО</th>
                            </tr>
                        </thead>
                        <tbody>
                            {salaries.map((salary) => (
                                <tr key={salary.agent_id} className="border-b border-border last:border-0">
                                    <td className="px-4 py-3 font-medium">{salary.agent_name}</td>
                                    <td className="px-4 py-3 text-right">{formatCurrency(salary.base_salary)}</td>
                                    <td className="px-4 py-3 text-right text-muted-foreground">
                                        {formatCurrency(salary.sales_amount)}
                                    </td>
                                    <td className="px-4 py-3 text-right text-muted-foreground">
                                        {salary.commission_rate}%
                                    </td>
                                    <td className="px-4 py-3 text-right text-green-500">
                                        +{formatCurrency(salary.commission)}
                                    </td>
                                    <td className="px-4 py-3 text-right text-green-500">
                                        {salary.bonus > 0 ? `+${formatCurrency(salary.bonus)}` : '—'}
                                    </td>
                                    <td className="px-4 py-3 text-right text-red-500">
                                        {salary.penalty > 0 ? `-${formatCurrency(salary.penalty)}` : '—'}
                                    </td>
                                    <td className="px-4 py-3 text-right font-bold">
                                        {formatCurrency(salary.total_salary)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                        <tfoot>
                            <tr className="bg-secondary/50">
                                <td className="px-4 py-3 font-bold">ИТОГО</td>
                                <td className="px-4 py-3 text-right font-medium">
                                    {formatCurrency(salaries.reduce((s, x) => s + x.base_salary, 0))}
                                </td>
                                <td className="px-4 py-3 text-right font-medium">
                                    {formatCurrency(totalSales)}
                                </td>
                                <td className="px-4 py-3"></td>
                                <td className="px-4 py-3 text-right font-medium text-green-500">
                                    +{formatCurrency(salaries.reduce((s, x) => s + x.commission, 0))}
                                </td>
                                <td className="px-4 py-3 text-right font-medium text-green-500">
                                    +{formatCurrency(salaries.reduce((s, x) => s + x.bonus, 0))}
                                </td>
                                <td className="px-4 py-3 text-right font-medium text-red-500">
                                    -{formatCurrency(salaries.reduce((s, x) => s + x.penalty, 0))}
                                </td>
                                <td className="px-4 py-3 text-right font-bold text-lg">
                                    {formatCurrency(totalSalary)}
                                </td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
        </div>
    );
}
