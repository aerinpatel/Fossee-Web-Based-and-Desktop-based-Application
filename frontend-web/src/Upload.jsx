import React, { useState, useRef } from 'react';
import api from './api';
import { CloudArrowUpIcon, DocumentIcon, CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';

/**
 * Upload component handles CSV file selection, drag-and-drop, 
 * and asynchronous upload to the Django backend.
 * 
 * @param {Object} props
 * @param {Function} props.onUploadSuccess - Callback triggered when analysis is complete.
 */
const Upload = ({ onUploadSuccess }) => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const inputRef = useRef(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
            setError(null);
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setError(null);
        }
    };

    const handleButtonClick = () => {
        inputRef.current.click();
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) {
            setError("Please select a file.");
            return;
        }

        const formData = new FormData();
        formData.append('csv_file', file);
        formData.append('name', file.name.replace('.csv', ''));

        setLoading(true);
        try {
            const response = await api.post('datasets/upload/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            onUploadSuccess(response.data);
            setFile(null);
        } catch (err) {
            console.error(err);
            let msg = "Upload failed. Ensure valid CSV.";

            if (err.response?.data) {
                if (err.response.data.error) msg = err.response.data.error;
                else if (err.response.data.detail) msg = err.response.data.detail;
                else msg = JSON.stringify(err.response.data);
            } else if (err.message) {
                msg = err.message;
            }
            setError(msg);

        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
                <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
                    <CloudArrowUpIcon className="h-6 w-6 mr-2 text-indigo-600" />
                    Upload Dataset
                </h3>

                <form onSubmit={handleUpload} onDragEnter={handleDrag} className="space-y-6">
                    <input
                        ref={inputRef}
                        type="file"
                        className="hidden"
                        accept=".csv"
                        onChange={handleChange}
                    />

                    <div
                        className={`relative border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center transition-all duration-200 cursor-pointer
                        ${dragActive
                                ? 'border-indigo-500 bg-indigo-50 scale-[1.01]'
                                : 'border-gray-300 hover:border-indigo-400 hover:bg-gray-50'
                            }
                        ${file ? 'bg-green-50 border-green-300' : ''}
                    `}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                        onClick={handleButtonClick}
                    >
                        {file ? (
                            <div className="text-center">
                                <DocumentIcon className="h-16 w-16 text-green-500 mx-auto mb-3" />
                                <p className="text-green-800 font-medium text-lg">{file.name}</p>
                                <p className="text-green-600 text-sm">{(file.size / 1024).toFixed(2)} KB</p>
                                <button
                                    type="button"
                                    onClick={(e) => { e.stopPropagation(); setFile(null); }}
                                    className="mt-4 text-xs font-semibold text-red-500 hover:text-red-700 uppercase tracking-wide"
                                >
                                    Remove File
                                </button>
                            </div>
                        ) : (
                            <div className="text-center">
                                <CloudArrowUpIcon className="h-16 w-16 text-indigo-400 mx-auto mb-3" />
                                <p className="text-lg font-medium text-gray-700 mb-1">
                                    Drag & drop your CSV file here
                                </p>
                                <p className="text-gray-400 text-sm mb-4">or click to browse</p>
                                <span className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                    Select File
                                </span>
                            </div>
                        )}
                    </div>

                    {error && (
                        <div className="flex items-center p-4 bg-red-50 rounded-lg text-red-700">
                            <ExclamationCircleIcon className="h-5 w-5 mr-2" />
                            <span className="text-sm font-medium">{error}</span>
                        </div>
                    )}

                    <div className="flex justify-end">
                        <button
                            type="submit"
                            disabled={loading || !file}
                            className={`flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg shadow-sm text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all
                            ${loading || !file
                                    ? 'bg-gray-300 cursor-not-allowed'
                                    : 'bg-indigo-600 hover:bg-indigo-700 hover:shadow-lg transform hover:-translate-y-0.5'
                                }
                        `}
                        >
                            {loading ? (
                                <>
                                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Uploading...
                                </>
                            ) : (
                                <>
                                    <CheckCircleIcon className="h-5 w-5 mr-2" />
                                    Start Analysis
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Upload;
