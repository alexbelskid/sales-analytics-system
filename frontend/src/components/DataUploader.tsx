'use client';

import { useState } from 'react';
import { useDropzone } from 'react-dropzone';

type UploadType = 'sales' | 'products' | 'customers';
type UploadMode = 'append' | 'replace';

export default function DataUploader() {
    const [activeTab, setActiveTab] = useState<UploadType>('sales');
    const [uploadMode, setUploadMode] = useState<UploadMode>('append');
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState<any>(null);

    const onDrop = async (acceptedFiles: File[]) => {
        if (acceptedFiles.length === 0) return;

        const file = acceptedFiles[0]; // Assuming single file upload based on maxFiles: 1
        setUploading(true);
        setResult(null);

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('mode', uploadMode);

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/data/upload/${activeTab}`, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            setResult(data);

            if (data.success || response.ok) {
                // Dispatch event to update dashboard
                window.dispatchEvent(new Event('dataUploaded'));
            }
        } catch (error) {
            setResult({ success: false, error: 'Upload failed' });
        } finally {
            setUploading(false);
        }
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'text/csv': ['.csv'] },
        maxFiles: 1,
    });

    const tabs = [
        { id: 'sales', label: '📊 Sales', icon: '📊' },
        { id: 'products', label: '📦 Products', icon: '📦' },
        { id: 'customers', label: '👥 Customers', icon: '👥' },
    ];

    return (
        <div className="bg-[#262626] rounded-lg p-6 mb-6 text-white border border-[#333333]">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Upload Data</h2>
                <div className="text-sm text-gray-400">
                    Supported format: CSV
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 mb-6">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => { setActiveTab(tab.id as UploadType); setResult(null); }}
                        className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${activeTab === tab.id
                                ? 'bg-white text-black font-medium'
                                : 'bg-[#333333] text-gray-300 hover:bg-[#3A3A3A]'
                            }`}
                    >
                        <span>{tab.icon}</span>
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Dropzone */}
            <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-200 ${isDragActive
                        ? 'border-green-500 bg-[#333333] scale-[1.01]'
                        : 'border-[#404040] hover:border-gray-500 hover:bg-[#222]'
                    }`}
            >
                <input {...getInputProps()} />
                <div className="flex flex-col items-center gap-3">
                    <div className="text-5xl mb-2 opacity-80">
                        {isDragActive ? '📂' : '📄'}
                    </div>
                    {isDragActive ? (
                        <p className="text-green-400 font-medium text-lg">Drop file here...</p>
                    ) : (
                        <>
                            <p className="text-lg font-medium">
                                Drag & drop CSV file here, or click to select
                            </p>
                            <p className="text-sm text-gray-500">
                                Upload {activeTab} data to update the analytics
                            </p>
                        </>
                    )}
                </div>
            </div>

            {/* Settings */}
            <div className="mt-6 flex flex-col md:flex-row gap-6 items-start md:items-center justify-between bg-[#222] p-4 rounded-lg">
                <div className="flex gap-6">
                    <label className="flex items-center gap-3 cursor-pointer group">
                        <div className={`w-5 h-5 rounded-full border flex items-center justify-center ${uploadMode === 'append' ? 'border-green-500' : 'border-gray-500'}`}>
                            {uploadMode === 'append' && <div className="w-2.5 h-2.5 rounded-full bg-green-500" />}
                        </div>
                        <input
                            type="radio"
                            name="mode"
                            value="append"
                            checked={uploadMode === 'append'}
                            onChange={(e) => setUploadMode(e.target.value as UploadMode)}
                            className="hidden"
                        />
                        <div className="flex flex-col">
                            <span className="text-sm font-medium group-hover:text-white transition-colors">Append</span>
                            <span className="text-xs text-gray-500">Add new records</span>
                        </div>
                    </label>

                    <label className="flex items-center gap-3 cursor-pointer group">
                        <div className={`w-5 h-5 rounded-full border flex items-center justify-center ${uploadMode === 'replace' ? 'border-red-500' : 'border-gray-500'}`}>
                            {uploadMode === 'replace' && <div className="w-2.5 h-2.5 rounded-full bg-red-500" />}
                        </div>
                        <input
                            type="radio"
                            name="mode"
                            value="replace"
                            checked={uploadMode === 'replace'}
                            onChange={(e) => setUploadMode(e.target.value as UploadMode)}
                            className="hidden"
                        />
                        <div className="flex flex-col">
                            <span className="text-sm font-medium group-hover:text-white transition-colors">Replace</span>
                            <span className="text-xs text-gray-500">Overwrite existing</span>
                        </div>
                    </label>
                </div>

                {/* Helper Text */}
                <div className="text-xs text-gray-500 bg-[#262626] px-3 py-1.5 rounded border border-[#333]">
                    Required columns:
                    {activeTab === 'sales' && <span className="text-gray-300 ml-1">date, customer_name, product_name, quantity, price, amount</span>}
                    {activeTab === 'products' && <span className="text-gray-300 ml-1">name, category, price</span>}
                    {activeTab === 'customers' && <span className="text-gray-300 ml-1">name, email, phone</span>}
                </div>
            </div>

            {/* Progress & Result */}
            {uploading && (
                <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg flex items-center gap-3 animate-pulse">
                    <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-blue-400 text-sm">Uploading and processing data...</span>
                </div>
            )}

            {result && (
                <div
                    className={`mt-4 p-4 rounded-lg border flex items-start gap-3 ${(result.success || result.rows_added !== undefined)
                            ? 'bg-green-500/10 border-green-500/20'
                            : 'bg-red-500/10 border-red-500/20'
                        }`}
                >
                    <span className="text-xl">{(result.success || result.rows_added !== undefined) ? '✅' : '❌'}</span>
                    <div>
                        {(result.success || result.rows_added !== undefined) ? (
                            <>
                                <p className="text-green-400 font-semibold text-sm">Upload Successful</p>
                                <p className="text-gray-400 text-xs mt-1">
                                    Added: {result.rows_added} rows
                                    {result.rows_skipped > 0 && ` • Skipped: ${result.rows_skipped} duplicates`}
                                </p>
                            </>
                        ) : (
                            <>
                                <p className="text-red-400 font-semibold text-sm">Upload Failed</p>
                                <p className="text-red-300/70 text-xs mt-1">{result.error || "Unknown error occurred"}</p>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
