'use client';

import React, { useState, useCallback } from 'react';
import {
    Upload,
    FileSpreadsheet,
    CheckCircle,
    XCircle,
    RefreshCw,
    AlertCircle,
    Info
} from 'lucide-react';
import LiquidButton from '@/components/LiquidButton';
import GlassSelect from '@/components/GlassSelect';
import GlassDatePicker from '@/components/GlassDatePicker';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://athletic-alignment-production-db41.up.railway.app';

interface UploadResult {
    success: boolean;
    import_id?: string;
    data_type?: string;
    imported_rows?: number;
    failed_rows?: number;
    message?: string;
    errors?: string[];
}

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [dataType, setDataType] = useState<string>('auto');
    const [mode, setMode] = useState<string>('append');
    const [periodStart, setPeriodStart] = useState<string>('');
    const [periodEnd, setPeriodEnd] = useState<string>('');
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState<UploadResult | null>(null);
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
            setResult(null);
        }
    }, []);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setResult(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setResult(null);

        try {
            const formData = new FormData();
            formData.append('file', file);

            if (dataType !== 'auto') {
                formData.append('data_type', dataType);
            }

            formData.append('mode', mode);

            if (periodStart) {
                formData.append('period_start', periodStart);
            }
            if (periodEnd) {
                formData.append('period_end', periodEnd);
            }

            const response = await fetch(`${API_BASE}/api/import/unified`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            setResult(data);

            if (data.success) {
                // Clear form on success
                setTimeout(() => {
                    setFile(null);
                    setResult(null);
                }, 3000);
            }
        } catch (error) {
            setResult({
                success: false,
                message: `Ошибка загрузки: ${error}`
            });
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="min-h-screen p-6">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-2xl font-bold flex items-center gap-3">
                        <Upload className="text-white" />
                        Загрузка данных
                    </h1>
                    <p className="text-gray-400 mt-1">
                        Загрузите данные о продажах, агентах, клиентах или товарах из файлов Excel или CSV
                    </p>
                </div>

                {/* Upload Area */}
                <div className="bg-card border border-border rounded-3xl p-8 mb-6">
                    {/* Drag and Drop Zone */}
                    <div
                        className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-200 ${dragActive
                            ? 'border-rose-500 bg-rose-500/10'
                            : 'border-gray-600 hover:border-rose-500/50'
                            }`}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                    >
                        <FileSpreadsheet className="mx-auto mb-4 text-gray-400" size={48} />

                        {file ? (
                            <div>
                                <p className="text-lg font-medium text-green-400 mb-2">
                                    {file.name}
                                </p>
                                <p className="text-sm text-gray-400">
                                    {(file.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                                <button
                                    onClick={() => setFile(null)}
                                    className="mt-4 text-sm text-red-400 hover:text-red-300"
                                >
                                    Удалить файл
                                </button>
                            </div>
                        ) : (
                            <div>
                                <p className="text-lg mb-2">
                                    Перетащите файл сюда
                                </p>
                                <p className="text-sm text-gray-400 mb-4">
                                    или
                                </p>
                                <div onClick={() => document.getElementById('file-upload-input')?.click()} className="flex justify-center">
                                    <LiquidButton
                                        icon={Upload}
                                    >
                                        Выбрать файл
                                    </LiquidButton>
                                    <input
                                        id="file-upload-input"
                                        type="file"
                                        accept=".xlsx,.xls,.csv"
                                        onChange={handleFileChange}
                                        className="hidden"
                                    />
                                </div>
                                <p className="text-xs text-gray-500 mt-4">
                                    Поддерживаемые форматы: Excel (.xlsx, .xls), CSV (.csv)
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Options */}
                    {file && (
                        <div className="mt-6 space-y-4">
                            {/* Data Type Selection */}
                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    Тип данных
                                </label>
                                <GlassSelect
                                    value={dataType}
                                    onChange={(e) => setDataType(e.target.value)}
                                >
                                    <option value="auto">Автоопределение</option>
                                    <option value="sales">Продажи</option>
                                    <option value="agents">Агенты</option>
                                    <option value="customers">Клиенты</option>
                                    <option value="products">Товары</option>
                                </GlassSelect>
                                <p className="text-xs text-gray-500 mt-1">
                                    Автоопределение проанализирует структуру файла для определения типа данных
                                </p>
                            </div>

                            {/* Mode Selection */}
                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    Режим импорта
                                </label>
                                <div className="flex gap-4">
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            value="append"
                                            checked={mode === 'append'}
                                            onChange={(e) => setMode(e.target.value)}
                                            className="text-rose-800 focus:ring-rose-800"
                                        />
                                        <span>Добавить (к существующим данным)</span>
                                    </label>
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            value="replace"
                                            checked={mode === 'replace'}
                                            onChange={(e) => setMode(e.target.value)}
                                            className="text-rose-800 focus:ring-rose-800"
                                        />
                                        <span>Заменить (очистить существующие данные)</span>
                                    </label>
                                </div>
                            </div>

                            {/* Period Selection (for agents) */}
                            {(dataType === 'agents' || dataType === 'auto') && (
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium mb-2">
                                            Начало периода (для агентов)
                                        </label>
                                        <GlassDatePicker
                                            value={periodStart}
                                            onChange={(date) => setPeriodStart(date)}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2">
                                            Конец периода (для агентов)
                                        </label>
                                        <GlassDatePicker
                                            value={periodEnd}
                                            onChange={(date) => setPeriodEnd(date)}
                                        />
                                    </div>
                                </div>
                            )}

                            {/* Upload Button */}
                            <LiquidButton
                                onClick={handleUpload}
                                disabled={uploading}
                                className="w-full"
                                icon={uploading ? RefreshCw : Upload}
                            >
                                {uploading ? 'Загрузка...' : 'Загрузить файл'}
                            </LiquidButton>
                        </div>
                    )}
                </div>

                {/* Result */}
                {result && (
                    <div
                        className={`border rounded-3xl p-6 ${result.success
                            ? 'bg-green-500/10 border-green-500/50'
                            : 'bg-red-500/10 border-red-500/50'
                            }`}
                    >
                        <div className="flex items-start gap-3">
                            {result.success ? (
                                <CheckCircle className="text-green-400 flex-shrink-0" size={24} />
                            ) : (
                                <XCircle className="text-red-400 flex-shrink-0" size={24} />
                            )}
                            <div className="flex-1">
                                <h3 className={`font-medium mb-2 ${result.success ? 'text-green-400' : 'text-red-400'}`}>
                                    {result.success ? 'Загрузка успешна' : 'Ошибка загрузки'}
                                </h3>
                                <p className="text-sm text-gray-300 mb-3">
                                    {result.message}
                                </p>
                                {result.success && (
                                    <div className="grid grid-cols-2 gap-4 text-sm">
                                        <div>
                                            <span className="text-gray-400">Тип данных:</span>
                                            <span className="ml-2 font-medium capitalize">{result.data_type}</span>
                                        </div>
                                        <div>
                                            <span className="text-gray-400">Импортировано строк:</span>
                                            <span className="ml-2 font-medium text-green-400">{result.imported_rows}</span>
                                        </div>
                                        {(result.failed_rows ?? 0) > 0 && (
                                            <div>
                                                <span className="text-gray-400">Ошибки:</span>
                                                <span className="ml-2 font-medium text-red-400">{result.failed_rows}</span>
                                            </div>
                                        )}
                                        {result.import_id && (
                                            <div className="col-span-2">
                                                <span className="text-gray-400">ID импорта:</span>
                                                <span className="ml-2 font-mono text-xs">{result.import_id}</span>
                                            </div>
                                        )}
                                    </div>
                                )}
                                {result.errors && result.errors.length > 0 && (
                                    <div className="mt-3">
                                        <p className="text-sm text-red-400 font-medium mb-1">Ошибки:</p>
                                        <ul className="text-xs text-gray-400 list-disc list-inside">
                                            {result.errors.map((error, idx) => (
                                                <li key={idx}>{error}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {/* Info Box */}
                <div className="mt-6 bg-blue-500/10 border border-blue-500/50 rounded-3xl p-6">
                    <div className="flex items-start gap-3">
                        <Info className="text-blue-400 flex-shrink-0" size={20} />
                        <div className="text-sm text-gray-300">
                            <p className="font-medium text-blue-400 mb-2">Как это работает:</p>
                            <ul className="space-y-1 list-disc list-inside">
                                <li>Загрузите файлы Excel или CSV с вашими данными</li>
                                <li>Функция автоопределения анализирует структуру файла</li>
                                <li>Все загрузки отслеживаются в менеджере файлов</li>
                                <li>Выберите «Добавить» для добавления данных или «Заменить» для полной замены</li>
                                <li>Просмотрите историю загрузок в <a href="/files" className="text-rose-400 hover:underline">Менеджере файлов</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
