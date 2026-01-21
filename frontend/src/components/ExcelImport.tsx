'use client';

import { useState, useRef, useEffect } from 'react';
import { Upload, FileSpreadsheet, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { importApi } from '@/lib/api';

interface ImportStatus {
    id: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    progress_percent: number;
    imported_rows: number;
    total_rows: number;
    failed_rows: number;
    error_log?: string;
}

import LiquidButton from './LiquidButton';

export function ExcelImport({ onComplete }: { onComplete?: () => void }) {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [importId, setImportId] = useState<string | null>(null);
    const [status, setStatus] = useState<ImportStatus | null>(null);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const pollRef = useRef<NodeJS.Timeout | null>(null);

    // Poll import status
    useEffect(() => {
        if (importId && status?.status !== 'completed' && status?.status !== 'failed') {
            pollRef.current = setInterval(async () => {
                try {
                    const newStatus = await importApi.getStatus(importId);
                    setStatus(newStatus);

                    if (newStatus.status === 'completed' || newStatus.status === 'failed') {
                        if (pollRef.current) clearInterval(pollRef.current);
                        if (newStatus.status === 'completed' && onComplete) {
                            onComplete();
                        }
                    }
                } catch (err) {
                    console.error('Status poll error:', err);
                }
            }, 2000);
        }

        return () => {
            if (pollRef.current) clearInterval(pollRef.current);
        };
    }, [importId, status?.status, onComplete]);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            if (!selectedFile.name.match(/\.(xlsx|xls)$/i)) {
                setError('Только Excel файлы (.xlsx, .xls)');
                return;
            }
            setFile(selectedFile);
            setError(null);
            setStatus(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setError(null);
        setStatus(null);

        try {
            const result = await importApi.uploadExcel(file);
            setImportId(result.import_id);
            setStatus({
                id: result.import_id,
                status: 'processing',
                progress_percent: 0,
                imported_rows: 0,
                total_rows: 0,
                failed_rows: 0
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Ошибка загрузки');
        } finally {
            setUploading(false);
        }
    };

    const formatFileSize = (bytes: number) => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    return (
        <div className="bg-[#202020] border border-[#333333] rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
                <FileSpreadsheet className="h-5 w-5 text-green-500" />
                <h3 className="font-semibold">Импорт Excel файла</h3>
            </div>

            {/* File Selection */}
            <div className="space-y-4">
                <div
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-[#333333] rounded-lg p-8 text-center cursor-pointer hover:border-[#404040] transition-colors"
                >
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".xlsx,.xls"
                        onChange={handleFileSelect}
                        className="hidden"
                    />

                    {file ? (
                        <div className="flex items-center justify-center gap-3">
                            <FileSpreadsheet className="h-8 w-8 text-green-500" />
                            <div className="text-left">
                                <p className="font-medium">{file.name}</p>
                                <p className="text-sm text-[#808080]">{formatFileSize(file.size)}</p>
                            </div>
                        </div>
                    ) : (
                        <>
                            <LiquidButton
                                icon={Upload}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    fileInputRef.current?.click();
                                }}
                            >
                                Выбрать Excel файл
                            </LiquidButton>
                            <p className="text-xs text-[#404040] mt-3">До 100 МБ, форматы .xlsx, .xls</p>
                        </>
                    )}
                </div>

                {/* Error */}
                {error && (
                    <div className="flex items-center gap-2 text-red-400 text-sm">
                        <XCircle className="h-4 w-4" />
                        {error}
                    </div>
                )}

                {/* Upload Button */}
                {file && !status && (
                    <LiquidButton
                        onClick={handleUpload}
                        disabled={uploading}
                        className="w-full"
                    >
                        {uploading ? (
                            <>
                                <Loader2 className="h-4 w-4 animate-spin" />
                                Загружается...
                            </>
                        ) : (
                            <>
                                <Upload className="h-4 w-4" />
                                Загрузить и импортировать
                            </>
                        )}
                    </LiquidButton>
                )}

                {/* Progress */}
                {status && (
                    <div className="space-y-3">
                        <div className="flex items-center justify-between text-sm">
                            <span className="text-[#808080]">
                                {status.status === 'processing' && 'Импортирование...'}
                                {status.status === 'completed' && 'Завершено!'}
                                {status.status === 'failed' && 'Ошибка импорта'}
                            </span>
                            <span className="font-medium">{status.progress_percent}%</span>
                        </div>

                        <div className="w-full bg-[#333333] rounded-full h-2">
                            <div
                                className={`h-2 rounded-full transition-all duration-300 ${status.status === 'completed' ? 'bg-green-500' :
                                    status.status === 'failed' ? 'bg-red-500' :
                                        'bg-blue-500'
                                    }`}
                                style={{ width: `${status.progress_percent}%` }}
                            />
                        </div>

                        <div className="flex justify-between text-xs text-[#808080]">
                            <span>Импортировано: {status.imported_rows.toLocaleString()} / {status.total_rows.toLocaleString()}</span>
                            {status.failed_rows > 0 && (
                                <span className="text-red-400">Ошибок: {status.failed_rows}</span>
                            )}
                        </div>

                        {status.status === 'completed' && (
                            <div className="flex items-center gap-2 text-green-400 text-sm">
                                <CheckCircle className="h-4 w-4" />
                                Импорт успешно завершён!
                            </div>
                        )}

                        {status.status === 'failed' && status.error_log && (
                            <div className="text-red-400 text-xs bg-red-950/50 p-2 rounded">
                                {status.error_log}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
