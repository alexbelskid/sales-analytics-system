'use client';

import { useState, useRef } from 'react';
import { Upload, FileSpreadsheet, Check, AlertCircle, Download } from 'lucide-react';
import { uploadApi } from '@/lib/api';

type DataType = 'sales' | 'customers' | 'products';

export default function UploadPage() {
    const [selectedType, setSelectedType] = useState<DataType>('sales');
    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const dataTypes = [
        { id: 'sales', name: 'Продажи', description: 'Загрузить данные о продажах' },
        { id: 'customers', name: 'Клиенты', description: 'Загрузить список клиентов' },
        { id: 'products', name: 'Товары', description: 'Загрузить каталог товаров' },
    ];

    async function handleUpload() {
        if (!file) return;

        setLoading(true);
        setResult(null);

        try {
            const response = await uploadApi.uploadExcel(file, selectedType);
            setResult({
                success: true,
                message: `Успешно загружено ${response.imported} из ${response.total} записей`,
            });
            setFile(null);
        } catch (err: any) {
            setResult({
                success: false,
                message: err.message || 'Ошибка загрузки файла',
            });
        } finally {
            setLoading(false);
        }
    }

    async function downloadTemplate() {
        try {
            const response = await uploadApi.getTemplate(selectedType);
            const blob = new Blob([response.template], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `template_${selectedType}.csv`;
            a.click();
        } catch (err) {
            console.error('Error downloading template:', err);
        }
    }

    return (
        <div className="mx-auto max-w-3xl space-y-6 animate-fade-in">
            <div>
                <h1 className="text-2xl font-bold">Загрузка данных</h1>
                <p className="text-muted-foreground">
                    Импортируйте данные из Excel или CSV файлов
                </p>
            </div>

            {/* Data Type Selection */}
            <div className="grid gap-4 md:grid-cols-3">
                {dataTypes.map((type) => (
                    <button
                        key={type.id}
                        onClick={() => setSelectedType(type.id as DataType)}
                        className={`rounded-xl border-2 p-4 text-left transition-all ${selectedType === type.id
                                ? 'border-primary bg-primary/5'
                                : 'border-border hover:border-primary/50'
                            }`}
                    >
                        <FileSpreadsheet className={`mb-2 h-6 w-6 ${selectedType === type.id ? 'text-primary' : 'text-muted-foreground'
                            }`} />
                        <p className="font-medium">{type.name}</p>
                        <p className="text-sm text-muted-foreground">{type.description}</p>
                    </button>
                ))}
            </div>

            {/* Upload Zone */}
            <div
                onClick={() => fileInputRef.current?.click()}
                className={`cursor-pointer rounded-xl border-2 border-dashed p-12 text-center transition-all ${file ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
                    }`}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".xlsx,.xls,.csv"
                    className="hidden"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                />
                <Upload className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
                {file ? (
                    <div>
                        <p className="font-medium text-primary">{file.name}</p>
                        <p className="text-sm text-muted-foreground">
                            {(file.size / 1024).toFixed(1)} KB
                        </p>
                    </div>
                ) : (
                    <div>
                        <p className="font-medium">Перетащите файл сюда</p>
                        <p className="text-sm text-muted-foreground">
                            или нажмите для выбора (Excel, CSV)
                        </p>
                    </div>
                )}
            </div>

            {/* Result Message */}
            {result && (
                <div className={`flex items-center gap-3 rounded-lg p-4 ${result.success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                    }`}>
                    {result.success ? (
                        <Check className="h-5 w-5" />
                    ) : (
                        <AlertCircle className="h-5 w-5" />
                    )}
                    {result.message}
                </div>
            )}

            {/* Actions */}
            <div className="flex gap-4">
                <button
                    onClick={handleUpload}
                    disabled={!file || loading}
                    className="flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 font-medium text-white transition-all hover:bg-primary/90 disabled:opacity-50"
                >
                    {loading ? 'Загрузка...' : 'Загрузить'}
                </button>
                <button
                    onClick={downloadTemplate}
                    className="flex items-center gap-2 rounded-lg border border-border px-6 py-2.5 font-medium transition-all hover:bg-secondary"
                >
                    <Download className="h-4 w-4" />
                    Скачать шаблон
                </button>
            </div>
        </div>
    );
}
