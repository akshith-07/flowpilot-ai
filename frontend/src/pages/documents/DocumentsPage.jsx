/**
 * DocumentsPage Component
 * Main page for document management with upload, filtering, and bulk operations
 */

import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CloudArrowUpIcon,
  DocumentIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';
import DataTable from '@/components/ui/DataTable';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Card from '@/components/ui/Card';
import Modal, { ConfirmModal } from '@/components/ui/Modal';
import { FormSelect } from '@/components/ui/Form';
import documentService from '@/services/documentService';
import { formatRelativeTime, formatFileSize } from '@/utils/formatters';
import toast from 'react-hot-toast';

/**
 * DocumentsPage Component
 */
export default function DocumentsPage() {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // File upload state
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, [typeFilter, statusFilter]);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const params = {};
      if (typeFilter) params.type = typeFilter;
      if (statusFilter) params.status = statusFilter;

      const response = await documentService.getDocuments(params);
      setDocuments(response.data || []);
    } catch (error) {
      toast.error(error.message || 'Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(files);
    setUploadModalOpen(true);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    const files = Array.from(e.dataTransfer.files);
    setSelectedFiles(files);
    setUploadModalOpen(true);
  }, []);

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      toast.error('Please select files to upload');
      return;
    }

    setIsUploading(true);
    const progress = {};

    try {
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        progress[file.name] = 0;
        setUploadProgress({ ...progress });

        await documentService.uploadDocument(file, (percent) => {
          progress[file.name] = percent;
          setUploadProgress({ ...progress });
        });

        progress[file.name] = 100;
        setUploadProgress({ ...progress });
      }

      toast.success(`Successfully uploaded ${selectedFiles.length} file(s)`);
      setUploadModalOpen(false);
      setSelectedFiles([]);
      setUploadProgress({});
      fetchDocuments();
    } catch (error) {
      toast.error(error.message || 'Failed to upload documents');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async () => {
    try {
      await documentService.deleteDocument(selectedDocument.id);
      toast.success('Document deleted successfully');
      setDeleteModalOpen(false);
      setSelectedDocument(null);
      fetchDocuments();
    } catch (error) {
      toast.error(error.message || 'Failed to delete document');
    }
  };

  const handleDownload = async (document) => {
    try {
      await documentService.downloadDocument(document.id);
      toast.success('Download started');
    } catch (error) {
      toast.error(error.message || 'Failed to download document');
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      processing: { variant: 'warning', label: 'Processing' },
      completed: { variant: 'success', label: 'Completed' },
      failed: { variant: 'error', label: 'Failed' },
      pending: { variant: 'secondary', label: 'Pending' },
    };
    const config = statusConfig[status] || statusConfig.pending;
    return <Badge variant={config.variant} dot>{config.label}</Badge>;
  };

  const getFileTypeIcon = (mimeType) => {
    return <DocumentIcon className="w-5 h-5 text-gray-400" />;
  };

  const getFileTypeBadge = (mimeType) => {
    const typeMap = {
      'application/pdf': 'PDF',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'XLSX',
      'text/csv': 'CSV',
      'image/png': 'PNG',
      'image/jpeg': 'JPG',
    };

    const type = typeMap[mimeType] || mimeType?.split('/')[1]?.toUpperCase() || 'FILE';
    return <Badge variant="secondary">{type}</Badge>;
  };

  const columns = [
    {
      key: 'name',
      label: 'Document',
      render: (value, row) => (
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0">
            {getFileTypeIcon(row.mime_type)}
          </div>
          <div className="flex flex-col">
            <span className="font-medium text-gray-900">{value}</span>
            <span className="text-xs text-gray-500">ID: {row.id?.slice(0, 8)}</span>
          </div>
        </div>
      ),
    },
    {
      key: 'mime_type',
      label: 'Type',
      render: (value) => getFileTypeBadge(value),
    },
    {
      key: 'file_size',
      label: 'Size',
      render: (value) => (
        <span className="text-sm text-gray-900">{formatFileSize(value)}</span>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => getStatusBadge(value),
    },
    {
      key: 'pages_count',
      label: 'Pages',
      render: (value) => (
        <span className="text-sm text-gray-900">{value || 'N/A'}</span>
      ),
    },
    {
      key: 'created_at',
      label: 'Uploaded',
      render: (value) => (
        <span className="text-sm text-gray-500">{formatRelativeTime(value)}</span>
      ),
    },
    {
      key: 'actions',
      label: 'Actions',
      sortable: false,
      render: (_, row) => (
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            leftIcon={ArrowDownTrayIcon}
            onClick={(e) => {
              e.stopPropagation();
              handleDownload(row);
            }}
            title="Download"
          />
          <Button
            variant="ghost"
            size="sm"
            leftIcon={TrashIcon}
            onClick={(e) => {
              e.stopPropagation();
              setSelectedDocument(row);
              setDeleteModalOpen(true);
            }}
            className="text-error-600 hover:text-error-700"
            title="Delete"
          />
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="mt-1 text-sm text-gray-500">
            Upload and process documents with AI-powered extraction
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <input
            type="file"
            id="file-upload"
            multiple
            accept=".pdf,.docx,.xlsx,.csv,.png,.jpg,.jpeg"
            onChange={handleFileSelect}
            className="hidden"
          />
          <label htmlFor="file-upload">
            <Button
              as="span"
              leftIcon={CloudArrowUpIcon}
            >
              Upload Documents
            </Button>
          </label>
        </div>
      </div>

      {/* Upload Drop Zone */}
      <Card
        className="border-2 border-dashed border-gray-300 bg-gray-50 hover:border-primary-400 transition-colors cursor-pointer"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <label htmlFor="file-upload" className="cursor-pointer">
          <div className="flex flex-col items-center justify-center py-8">
            <CloudArrowUpIcon className="w-12 h-12 text-gray-400 mb-4" />
            <p className="text-sm text-gray-600">
              <span className="font-medium text-primary-600 hover:text-primary-500">
                Click to upload
              </span>
              {' '}or drag and drop files here
            </p>
            <p className="text-xs text-gray-500 mt-2">
              PDF, DOCX, XLSX, CSV, PNG, JPG (max 50MB each)
            </p>
          </div>
        </label>
      </Card>

      {/* Filters */}
      <div className="flex items-center space-x-4">
        <FormSelect
          placeholder="All Types"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          options={[
            { label: 'PDF', value: 'application/pdf' },
            { label: 'Word Documents', value: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' },
            { label: 'Excel Spreadsheets', value: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' },
            { label: 'CSV', value: 'text/csv' },
            { label: 'Images', value: 'image' },
          ]}
          className="w-48"
        />
        <FormSelect
          placeholder="All Statuses"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          options={[
            { label: 'Pending', value: 'pending' },
            { label: 'Processing', value: 'processing' },
            { label: 'Completed', value: 'completed' },
            { label: 'Failed', value: 'failed' },
          ]}
          className="w-48"
        />
      </div>

      {/* Documents Table */}
      <DataTable
        data={documents}
        columns={columns}
        loading={loading}
        searchable
        pagination
        onRowClick={(row) => navigate(`/documents/${row.id}`)}
        emptyMessage="No documents found. Upload your first document to get started."
      />

      {/* Upload Modal */}
      <Modal
        isOpen={uploadModalOpen}
        onClose={() => !isUploading && setUploadModalOpen(false)}
        title="Upload Documents"
        size="lg"
      >
        <div className="space-y-4">
          {selectedFiles.length > 0 ? (
            <div className="space-y-3">
              <p className="text-sm text-gray-600">
                {selectedFiles.length} file(s) selected
              </p>
              <div className="max-h-96 overflow-y-auto space-y-2">
                {selectedFiles.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center space-x-3 flex-1">
                      <DocumentIcon className="w-5 h-5 text-gray-400" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatFileSize(file.size)}
                        </p>
                      </div>
                    </div>
                    {uploadProgress[file.name] !== undefined && (
                      <div className="ml-4 w-24">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full transition-all"
                            style={{ width: `${uploadProgress[file.name]}%` }}
                          />
                        </div>
                        <p className="text-xs text-gray-600 text-center mt-1">
                          {uploadProgress[file.name]}%
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-600">No files selected</p>
          )}
        </div>
        <div className="mt-6 flex justify-end space-x-3">
          <Button
            variant="outline"
            onClick={() => setUploadModalOpen(false)}
            disabled={isUploading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleUpload}
            loading={isUploading}
            leftIcon={CloudArrowUpIcon}
          >
            Upload
          </Button>
        </div>
      </Modal>

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        onConfirm={handleDelete}
        title="Delete Document"
        message={`Are you sure you want to delete "${selectedDocument?.name}"? This action cannot be undone.`}
        confirmText="Delete"
        variant="danger"
      />
    </div>
  );
}
