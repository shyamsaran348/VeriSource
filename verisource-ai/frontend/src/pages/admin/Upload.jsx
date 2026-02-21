import React, { useState } from 'react';
import { documentService } from '../../services/documentService';
import LoaderPipeline from '../../components/LoaderPipeline';
import { UploadCloud, File, AlertCircle, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';

const Upload = () => {
    const [file, setFile] = useState(null);
    const [mode, setMode] = useState('policy');
    const [version, setVersion] = useState('1.0');
    const [authority, setAuthority] = useState('');

    const [isUploading, setIsUploading] = useState(false);
    const [uploadStep, setUploadStep] = useState(0); // 0: not started, 1-4: pipeline, 5: complete
    const [uploadProgress, setUploadProgress] = useState(0);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setError(null);
        }
    };

    const simulateProgress = () => {
        setUploadStep(1);

        // Simulate pipeline steps for UI effect while actual upload happens
        let currentStep = 1;
        let currentProgress = 0;

        const interval = setInterval(() => {
            if (currentStep < 4) {
                currentProgress += Math.random() * 15;
                if (currentProgress > 95) {
                    currentStep++;
                    currentProgress = 0;
                    setUploadStep(currentStep);
                }
                setUploadProgress(Math.min(Math.round(currentProgress), 99));
            } else {
                clearInterval(interval);
            }
        }, 400);

        return interval;
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) {
            setError('Please select a document to upload.');
            return;
        }

        if (!authority && mode === 'policy') {
            setError('Policy documents require an explicit Authority source.');
            return;
        }

        setIsUploading(true);
        setError(null);
        setSuccess(false);

        const progressInterval = simulateProgress();

        try {
            const documentName = file.name.replace(/\.[^/.]+$/, ""); // Strip extension
            await documentService.uploadDocument(file, documentName, mode, version, authority || 'Standard');

            // Force completion
            clearInterval(progressInterval);
            setUploadStep(5);
            setUploadProgress(100);
            setSuccess(true);

            // Reset form
            setTimeout(() => {
                setFile(null);
                setVersion('1.0');
                setAuthority('');
                setUploadStep(0);
                setUploadProgress(0);
                setIsUploading(false);
            }, 3000);

        } catch (err) {
            clearInterval(progressInterval);
            setIsUploading(false);
            setUploadStep(0);
            setUploadProgress(0);

            let errMsg = 'Upload failed. The document may be corrupted or not properly formatted.';
            if (err.response?.data?.detail) {
                if (Array.isArray(err.response.data.detail)) {
                    errMsg = err.response.data.detail.map(d => d.msg).join(', ');
                } else if (typeof err.response.data.detail === 'string') {
                    errMsg = err.response.data.detail;
                }
            } else if (typeof err.response?.data === 'string') {
                errMsg = err.response.data;
            }

            setError(errMsg);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <div>
                <h1 className="text-3xl font-bold tracking-tight mb-2">Knowledge Ingestion</h1>
                <p className="text-gray-400">Upload documents into the isolated vector store.</p>
            </div>

            {error && (
                <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="p-4 bg-red-500/10 border border-red-500/20 text-red-200 text-sm rounded-xl flex gap-3"
                >
                    <AlertCircle className="w-5 h-5 flex-shrink-0 text-red-400 -mt-0.5" />
                    <p className="leading-relaxed">
                        {typeof error === 'string' ? error : JSON.stringify(error)}
                    </p>
                </motion.div>
            )}

            {success && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="p-4 bg-green-500/10 border border-green-500/20 text-green-200 text-sm rounded-xl flex items-center gap-3"
                >
                    <CheckCircle2 className="w-5 h-5 flex-shrink-0 text-green-400" />
                    <p>Document successfully ingested and indexed for retrieval.</p>
                </motion.div>
            )}

            {uploadStep > 0 && uploadStep < 5 ? (
                <div className="mt-8">
                    <LoaderPipeline step={uploadStep} progress={uploadProgress} />
                </div>
            ) : (
                <form onSubmit={handleUpload} className="grid grid-cols-1 md:grid-cols-12 gap-8">
                    {/* Left: Configuration */}
                    <div className="md:col-span-5 space-y-6 bg-brand-navy-light/30 border border-white/5 p-6 rounded-2xl backdrop-blur-sm">
                        <div>
                            <label className="text-sm font-semibold text-gray-400 uppercase tracking-widest block mb-3">Verification Mode</label>
                            <div className="flex bg-brand-navy rounded-lg p-1 border border-white/5">
                                <button
                                    type="button"
                                    onClick={() => setMode('policy')}
                                    className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${mode === 'policy'
                                        ? 'bg-blue-500 text-white shadow'
                                        : 'text-gray-400 hover:text-white'
                                        }`}
                                >
                                    Policy
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setMode('research')}
                                    className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${mode === 'research'
                                        ? 'bg-purple-500 text-white shadow'
                                        : 'text-gray-400 hover:text-white'
                                        }`}
                                >
                                    Research
                                </button>
                            </div>
                        </div>

                        <div>
                            <label className="text-sm font-semibold text-gray-400 uppercase tracking-widest block mb-2">Version Alignment</label>
                            <input
                                type="text"
                                value={version}
                                onChange={(e) => setVersion(e.target.value)}
                                className="w-full bg-brand-navy border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-gold/50"
                                placeholder="e.g. 1.0, 2024-A"
                                required
                            />
                        </div>

                        <div>
                            <label className="text-sm font-semibold text-gray-400 uppercase tracking-widest block mb-2 flex justify-between">
                                <span>Issuing Authority</span>
                                {mode === 'policy' && <span className="text-red-400 text-[10px]">*Required</span>}
                            </label>
                            <input
                                type="text"
                                value={authority}
                                onChange={(e) => setAuthority(e.target.value)}
                                className={`w-full bg-brand-navy border rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-gold/50 ${mode === 'policy' && !authority ? 'border-red-500/50' : 'border-white/10'
                                    }`}
                                placeholder="e.g. HR Dept, Academic Board"
                            />
                        </div>
                    </div>

                    {/* Right: File Drop */}
                    <div className="md:col-span-7 flex flex-col">
                        <div
                            className={`flex-1 min-h-[300px] border-2 border-dashed rounded-2xl flex flex-col items-center justify-center p-8 transition-all ${file
                                ? 'border-gold bg-gold/5'
                                : 'border-white/20 bg-brand-navy-light/10 hover:border-white/40 hover:bg-white/5'
                                }`}
                        >
                            <input
                                type="file"
                                id="fileUpload"
                                onChange={handleFileChange}
                                className="hidden"
                                accept=".pdf,.txt,.md"
                            />

                            {file ? (
                                <div className="text-center">
                                    <div className="w-16 h-16 mx-auto bg-gold/20 text-gold rounded-full flex items-center justify-center mb-4">
                                        <File className="w-8 h-8" />
                                    </div>
                                    <h3 className="text-xl font-bold text-white mb-2">{file.name}</h3>
                                    <p className="text-gray-400 mb-6 flex gap-3 justify-center text-sm">
                                        <span>{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                                        <span>&bull;</span>
                                        <span className="uppercase">{file.name.split('.').pop()}</span>
                                    </p>
                                    <button
                                        type="button"
                                        onClick={() => setFile(null)}
                                        className="text-sm text-gray-400 hover:text-white underline decoration-dashed"
                                    >
                                        Choose different file
                                    </button>
                                </div>
                            ) : (
                                <label htmlFor="fileUpload" className="cursor-pointer text-center w-full h-full flex flex-col items-center justify-center">
                                    <div className="w-16 h-16 mx-auto bg-brand-navy text-gray-400 rounded-full flex items-center justify-center mb-4 border border-white/10 shadow-lg">
                                        <UploadCloud className="w-8 h-8" />
                                    </div>
                                    <h3 className="text-xl font-bold text-white mb-2">Select Corpus File</h3>
                                    <p className="text-gray-400 mb-8 max-w-xs mx-auto text-sm leading-relaxed">
                                        Support for PDF and Text documents. Processing automatically strictly isolates and chunks the file.
                                    </p>
                                    <span className="bg-brand-navy py-2 px-6 rounded-lg text-sm font-medium text-white border border-white/10 hover:border-gold transition-colors inline-block">
                                        Browse Files
                                    </span>
                                </label>
                            )}
                        </div>

                        <div className="mt-6 flex justify-end">
                            <button
                                type="submit"
                                disabled={isUploading || !file || (mode === 'policy' && !authority)}
                                className="px-8 py-3 bg-gold hover:bg-yellow-500 text-brand-navy font-bold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                            >
                                Initiate Ingestion
                            </button>
                        </div>
                    </div>
                </form>
            )}
        </div>
    );
};

export default Upload;
