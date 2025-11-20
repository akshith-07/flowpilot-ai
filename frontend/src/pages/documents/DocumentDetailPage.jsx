/**
 * DocumentDetailPage Component
 * Detailed view of a document with metadata, OCR results, and entity extraction
 */

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon,
  ArrowDownTrayIcon,
  DocumentTextIcon,
  TableCellsIcon,
  TagIcon,
  ClockIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Card, { CardHeader, CardTitle, CardDescription, CardBody } from '@/components/ui/Card';
import { ConfirmModal } from '@/components/ui/Modal';
import documentService from '@/services/documentService';
import { formatDate, formatFileSize } from '@/utils/formatters';
import toast from 'react-hot-toast';

/**
 * DocumentDetailPage Component
 */
export default function DocumentDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('metadata');

  useEffect(() => {
    fetchDocument();
  }, [id]);

  const fetchDocument = async () => {
    try {
      setLoading(true);
      const response = await documentService.getDocumentById(id);
      setDocument(response.data);
    } catch (error) {
      toast.error(error.message || 'Failed to fetch document');
      navigate('/documents');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      await documentService.downloadDocument(id);
      toast.success('Download started');
    } catch (error) {
      toast.error(error.message || 'Failed to download document');
    }
  };

  const handleDelete = async () => {
    try {
      await documentService.deleteDocument(id);
      toast.success('Document deleted successfully');
      navigate('/documents');
    } catch (error) {
      toast.error(error.message || 'Failed to delete document');
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

  const tabs = [
    { id: 'metadata', label: 'Metadata', icon: DocumentTextIcon },
    { id: 'ocr', label: 'OCR Text', icon: DocumentTextIcon },
    { id: 'entities', label: 'Entities', icon: TagIcon },
    { id: 'tables', label: 'Tables', icon: TableCellsIcon },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!document) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            leftIcon={ArrowLeftIcon}
            onClick={() => navigate('/documents')}
          >
            Back
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{document.name}</h1>
            <p className="mt-1 text-sm text-gray-500">
              Document ID: {document.id}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            leftIcon={ArrowDownTrayIcon}
            onClick={handleDownload}
          >
            Download
          </Button>
          <Button
            variant="danger"
            leftIcon={TrashIcon}
            onClick={() => setDeleteModalOpen(true)}
          >
            Delete
          </Button>
        </div>
      </div>

      {/* Document Info Card */}
      <Card>
        <CardBody>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm font-medium text-gray-500">Status</p>
              <div className="mt-1">{getStatusBadge(document.status)}</div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">File Size</p>
              <p className="mt-1 text-sm text-gray-900">{formatFileSize(document.file_size)}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Pages</p>
              <p className="mt-1 text-sm text-gray-900">{document.pages_count || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Uploaded</p>
              <p className="mt-1 text-sm text-gray-900">{formatDate(document.created_at)}</p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm
                  ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Metadata Tab */}
        {activeTab === 'metadata' && (
          <Card>
            <CardHeader>
              <CardTitle>Document Metadata</CardTitle>
              <CardDescription>
                Information extracted from the document
              </CardDescription>
            </CardHeader>
            <CardBody>
              <dl className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <dt className="text-sm font-medium text-gray-500">File Name</dt>
                  <dd className="mt-1 text-sm text-gray-900">{document.name}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">MIME Type</dt>
                  <dd className="mt-1 text-sm text-gray-900">{document.mime_type}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">File Size</dt>
                  <dd className="mt-1 text-sm text-gray-900">{formatFileSize(document.file_size)}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Pages</dt>
                  <dd className="mt-1 text-sm text-gray-900">{document.pages_count || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Created At</dt>
                  <dd className="mt-1 text-sm text-gray-900">{formatDate(document.created_at)}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Updated At</dt>
                  <dd className="mt-1 text-sm text-gray-900">{formatDate(document.updated_at)}</dd>
                </div>
                {document.metadata && Object.keys(document.metadata).length > 0 && (
                  <>
                    {Object.entries(document.metadata).map(([key, value]) => (
                      <div key={key}>
                        <dt className="text-sm font-medium text-gray-500">{key}</dt>
                        <dd className="mt-1 text-sm text-gray-900">{String(value)}</dd>
                      </div>
                    ))}
                  </>
                )}
              </dl>
            </CardBody>
          </Card>
        )}

        {/* OCR Text Tab */}
        {activeTab === 'ocr' && (
          <Card>
            <CardHeader>
              <CardTitle>Extracted Text (OCR)</CardTitle>
              <CardDescription>
                Text content extracted from the document
              </CardDescription>
            </CardHeader>
            <CardBody>
              {document.extracted_text ? (
                <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <pre className="text-sm text-gray-900 whitespace-pre-wrap font-mono">
                    {document.extracted_text}
                  </pre>
                </div>
              ) : (
                <div className="text-center py-12">
                  <DocumentTextIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-sm text-gray-500">
                    {document.status === 'completed'
                      ? 'No text extracted from this document'
                      : 'Text extraction in progress...'}
                  </p>
                </div>
              )}
            </CardBody>
          </Card>
        )}

        {/* Entities Tab */}
        {activeTab === 'entities' && (
          <Card>
            <CardHeader>
              <CardTitle>Extracted Entities</CardTitle>
              <CardDescription>
                Named entities and key information extracted from the document
              </CardDescription>
            </CardHeader>
            <CardBody>
              {document.entities && document.entities.length > 0 ? (
                <div className="space-y-4">
                  {document.entities.map((entity, index) => (
                    <div
                      key={index}
                      className="flex items-start justify-between p-4 bg-gray-50 rounded-lg"
                    >
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <Badge variant="primary">{entity.type}</Badge>
                          <span className="text-sm font-medium text-gray-900">
                            {entity.text}
                          </span>
                        </div>
                        {entity.confidence && (
                          <p className="mt-1 text-xs text-gray-500">
                            Confidence: {(entity.confidence * 100).toFixed(1)}%
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <TagIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-sm text-gray-500">
                    {document.status === 'completed'
                      ? 'No entities extracted from this document'
                      : 'Entity extraction in progress...'}
                  </p>
                </div>
              )}
            </CardBody>
          </Card>
        )}

        {/* Tables Tab */}
        {activeTab === 'tables' && (
          <Card>
            <CardHeader>
              <CardTitle>Extracted Tables</CardTitle>
              <CardDescription>
                Structured table data extracted from the document
              </CardDescription>
            </CardHeader>
            <CardBody>
              {document.tables && document.tables.length > 0 ? (
                <div className="space-y-6">
                  {document.tables.map((table, tableIndex) => (
                    <div key={tableIndex} className="overflow-x-auto">
                      <h4 className="text-sm font-medium text-gray-900 mb-3">
                        Table {tableIndex + 1}
                        {table.page && ` (Page ${table.page})`}
                      </h4>
                      <table className="min-w-full divide-y divide-gray-200 border border-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            {table.headers?.map((header, headerIndex) => (
                              <th
                                key={headerIndex}
                                className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                              >
                                {header}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {table.rows?.map((row, rowIndex) => (
                            <tr key={rowIndex} className="hover:bg-gray-50">
                              {row.map((cell, cellIndex) => (
                                <td
                                  key={cellIndex}
                                  className="px-4 py-2 text-sm text-gray-900"
                                >
                                  {cell}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <TableCellsIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-sm text-gray-500">
                    {document.status === 'completed'
                      ? 'No tables found in this document'
                      : 'Table extraction in progress...'}
                  </p>
                </div>
              )}
            </CardBody>
          </Card>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        onConfirm={handleDelete}
        title="Delete Document"
        message={`Are you sure you want to delete "${document.name}"? This action cannot be undone.`}
        confirmText="Delete"
        variant="danger"
      />
    </div>
  );
}
