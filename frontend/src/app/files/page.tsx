'use client';

import React, { useState, useEffect } from 'react';
import {
    FileSpreadsheet,
    Trash2,
    Eye,
    RefreshCw,
    CheckCircle,
    XCircle,
    Clock,
    Download,
    AlertTriangle
} from 'lucide-react';

interface ImportFile {
    id: string;
    filename: string;
    uploaded_at: string;
    status: 'completed' | 'failed' | 'processing' | 'pending';
    file_size_mb: number;
    total_rows: number;
    imported_rows: number;
    failed_rows: number;
    progress: number;
    period: string;
    error?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function FilesPage() {
    const [files, setFiles] = useState<ImportFile[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedFile, setSelectedFile] = useState<ImportFile | null>(null);
    const [statusFilter, setStatusFilter] = useState<string>('');

    const fetchFiles = async () => {
        try {
            const params = new URLSearchParams();
            if (statusFilter) params.append('status', statusFilter);

            const res = await fetch(`${API_BASE}/api/files/list?${params}`);
            const data = await res.json();
            setFiles(data.files || []);
        } catch (err) {
            console.error('Failed to fetch files:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchFiles();
        // Auto-refresh if any file is processing
        const interval = setInterval(() => {
            if (files.some(f => f.status === 'processing')) {
                fetchFiles();
            }
        }, 5000);
        return () => clearInterval(interval);
    }, [statusFilter]);

    const handleDelete = async (id: string) => {
        if (!confirm('Удалить запись об импорте?')) return;

        try {
            await fetch(`${API_BASE}/api/files/${id}`, { method: 'DELETE' });
            fetchFiles();
        } catch (err) {
            console.error('Delete failed:', err);
        }
    };

    const clearCache = async () => {
        try {
            await fetch(`${API_BASE}/api/files/clear-cache`, { method: 'POST' });
            alert('Кэш аналитики очищен');
        } catch (err) {
            console.error('Clear cache failed:', err);
        }
    };

    const resetStuck = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/files/reset-stuck`, { method: 'POST' });
            const data = await res.json();
            if (data.reset_count > 0) {
                alert(`Сброшено ${data.reset_count} застрявших импортов`);
            } else {
                alert('Нет застрявших импортов');
            }
            fetchFiles();
        } catch (err) {
            console.error('Reset stuck failed:', err);
        }
    };

    const deleteAllData = async () => {
        if (!confirm('⚠️ УДАЛИТЬ ВСЕ ДАННЫЕ ПРОДАЖ?\\n\\nЭто действие нельзя отменить!')) return;
        if (!confirm('Вы уверены? Все данные будут удалены безвозвратно.')) return;

        try {
            const res = await fetch(`${API_BASE}/api/files/all-sales`, { method: 'DELETE' });
            const data = await res.json();
            alert(`Удалено ${data.deleted_count} записей`);
            fetchFiles();
        } catch (err) {
            console.error('Delete all failed:', err);
            alert('Ошибка при удалении');
        }
    };

    const formatDate = (dateStr: string) => {
        if (!dateStr) return '—';
        return new Date(dateStr).toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const StatusBadge = ({ status }: { status: string }) => {
        const styles: Record<string, { bg: string; text: string; icon: React.ReactNode }> = {
            completed: { bg: 'bg-green-500/20', text: 'text-green-400', icon: <CheckCircle size={14} /> },
            failed: { bg: 'bg-red-500/20', text: 'text-red-400', icon: <XCircle size={14} /> },
            processing: { bg: 'bg-blue-500/20', text: 'text-blue-400', icon: <RefreshCw size={14} className="animate-spin" /> },
            pending: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', icon: <Clock size={14} /> }
        };

        const style = styles[status] || styles.pending;

        return (
            <span className={`flex items-center gap-1 px-2 py-1 rounded text-xs ${style.bg} ${style.text}`}>
                {style.icon}
                {status === 'completed' ? 'Готово' :
                    status === 'failed' ? 'Ошибка' :
                        status === 'processing' ? 'Импорт...' : 'Ожидание'}
            </span>
        );
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white p-6">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-2xl font-bold flex items-center gap-3">
                            <FileSpreadsheet className="text-blue-400" />
                            Управление файлами
                        </h1>
                        <p className="text-gray-400 mt-1">История импортов и загруженные данные</p>
                    </div>

                    <div className="flex gap-3 flex-wrap">
                        <button
                            onClick={resetStuck}
                            className="flex items-center gap-2 px-4 py-2 bg-yellow-600 hover:bg-yellow-500 rounded-lg transition"
                        >
                            <AlertTriangle size={16} />
                            Сбросить застрявшие
                        </button>
                        <button
                            onClick={deleteAllData}
                            className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 rounded-lg transition"
                        >
                            <Trash2 size={16} />
                            Удалить ВСЕ данные
                        </button>
                        <button
                            onClick={clearCache}
                            className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
                        >
                            <RefreshCw size={16} />
                            Очистить кэш
                        </button>
                        <button
                            onClick={fetchFiles}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg transition"
                        >
                            <RefreshCw size={16} />
                            Обновить
                        </button>
                    </div>
                </div>

                {/* Filters */}
                <div className="flex gap-4 mb-6">
                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm"
                    >
                        <option value="">Все статусы</option>
                        <option value="completed">Завершённые</option>
                        <option value="failed">С ошибками</option>
                        <option value="processing">В процессе</option>
                    </select>
                </div>

                {/* Table */}
                <div className="bg-gray-800 rounded-xl overflow-hidden">
                    <table className="w-full">
                        <thead className="bg-gray-700/50">
                            <tr>
                                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Файл</th>
                                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Дата</th>
                                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Статус</th>
                                <th className="text-right px-6 py-4 text-sm font-medium text-gray-400">Размер</th>
                                <th className="text-right px-6 py-4 text-sm font-medium text-gray-400">Записей</th>
                                <th className="text-center px-6 py-4 text-sm font-medium text-gray-400">Действия</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-700">
                            {loading ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-12 text-center text-gray-400">
                                        <RefreshCw className="animate-spin mx-auto mb-2" />
                                        Загрузка...
                                    </td>
                                </tr>
                            ) : files.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-12 text-center text-gray-400">
                                        Нет загруженных файлов
                                    </td>
                                </tr>
                            ) : (
                                files.map((file) => (
                                    <tr key={file.id} className="hover:bg-gray-700/30 transition">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <FileSpreadsheet className="text-green-400" size={20} />
                                                <div>
                                                    <div className="font-medium truncate max-w-[200px]" title={file.filename}>
                                                        {file.filename}
                                                    </div>
                                                    {file.error && (
                                                        <div className="text-xs text-red-400 flex items-center gap-1 mt-1">
                                                            <AlertTriangle size={12} />
                                                            {file.error.substring(0, 50)}...
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-400">
                                            {formatDate(file.uploaded_at)}
                                        </td>
                                        <td className="px-6 py-4">
                                            <StatusBadge status={file.status} />
                                            {file.status === 'processing' && (
                                                <div className="mt-2 w-full bg-gray-700 rounded-full h-1.5">
                                                    <div
                                                        className="bg-blue-500 h-1.5 rounded-full transition-all"
                                                        style={{ width: `${file.progress}%` }}
                                                    />
                                                </div>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 text-right text-sm">
                                            {file.file_size_mb.toFixed(1)} МБ
                                        </td>
                                        <td className="px-6 py-4 text-right text-sm">
                                            <div>{file.imported_rows.toLocaleString()}</div>
                                            {file.failed_rows > 0 && (
                                                <div className="text-xs text-red-400">
                                                    {file.failed_rows} ошибок
                                                </div>
                                            )}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center justify-center gap-2">
                                                <button
                                                    onClick={() => setSelectedFile(file)}
                                                    className="p-2 hover:bg-gray-600 rounded-lg transition"
                                                    title="Подробнее"
                                                >
                                                    <Eye size={16} className="text-gray-400" />
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(file.id)}
                                                    className="p-2 hover:bg-red-500/20 rounded-lg transition"
                                                    title="Удалить"
                                                >
                                                    <Trash2 size={16} className="text-red-400" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Details Modal */}
                {selectedFile && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                        <div className="bg-gray-800 rounded-xl p-6 max-w-lg w-full mx-4">
                            <h3 className="text-xl font-bold mb-4">Детали импорта</h3>

                            <div className="space-y-3 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Файл:</span>
                                    <span className="font-medium">{selectedFile.filename}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Статус:</span>
                                    <StatusBadge status={selectedFile.status} />
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Размер:</span>
                                    <span>{selectedFile.file_size_mb.toFixed(2)} МБ</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Всего строк:</span>
                                    <span>{selectedFile.total_rows.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Импортировано:</span>
                                    <span className="text-green-400">{selectedFile.imported_rows.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Ошибок:</span>
                                    <span className="text-red-400">{selectedFile.failed_rows}</span>
                                </div>
                                {selectedFile.error && (
                                    <div className="mt-4 p-3 bg-red-500/10 rounded-lg text-red-400 text-xs">
                                        <strong>Ошибка:</strong> {selectedFile.error}
                                    </div>
                                )}
                            </div>

                            <button
                                onClick={() => setSelectedFile(null)}
                                className="mt-6 w-full py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
                            >
                                Закрыть
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
