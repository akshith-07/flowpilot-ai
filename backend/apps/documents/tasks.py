"""
Celery tasks for Documents app.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_document(self, document_id, extract_text=True, generate_embeddings=False):
    """
    Process uploaded document (OCR, extraction, embeddings).

    Args:
        document_id: Document ID
        extract_text: Whether to extract text using OCR
        generate_embeddings: Whether to generate embeddings
    """
    try:
        from .models import Document, DocumentPage
        from django.utils import timezone
        import PyMuPDF  # fitz
        from PIL import Image
        import pytesseract

        document = Document.objects.get(id=document_id)

        # Update status
        document.status = 'processing'
        document.save(update_fields=['status'])

        # Process based on file type
        if document.file_type == 'pdf':
            # Extract text from PDF
            if extract_text:
                doc = PyMuPDF.open(document.file_path)

                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text()

                    DocumentPage.objects.create(
                        document=document,
                        page_number=page_num + 1,
                        text_content=text,
                        ocr_confidence=1.0,  # Direct PDF extraction
                        metadata={'source': 'pdf_text'}
                    )

                document.page_count = len(doc)
                doc.close()

        elif document.file_type == 'image':
            # OCR for images
            if extract_text:
                # Use pytesseract for OCR
                image = Image.open(document.file_path)
                text = pytesseract.image_to_string(image)

                DocumentPage.objects.create(
                    document=document,
                    page_number=1,
                    text_content=text,
                    ocr_confidence=0.85,  # Estimate
                    metadata={'source': 'ocr'}
                )

                document.page_count = 1

        # Generate embeddings if requested
        if generate_embeddings:
            from .tasks import generate_document_embeddings
            generate_document_embeddings.delay(document_id)

        # Mark as completed
        document.status = 'completed'
        document.processed_at = timezone.now()
        document.save(update_fields=['status', 'processed_at', 'page_count'])

        logger.info(f'Document processed successfully: {document_id}')

    except Exception as e:
        logger.error(f'Document processing failed: {str(e)}')

        # Update status to failed
        try:
            document = Document.objects.get(id=document_id)
            document.status = 'failed'
            document.metadata['error'] = str(e)
            document.save(update_fields=['status', 'metadata'])
        except:
            pass

        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def extract_document_data(self, document_id, extraction_type, extraction_config=None):
    """
    Extract structured data from document using AI.

    Args:
        document_id: Document ID
        extraction_type: Type of extraction
        extraction_config: Configuration for extraction
    """
    try:
        from .models import Document, DocumentExtraction
        from apps.ai_engine.services import AIService

        document = Document.objects.get(id=document_id)
        extraction_config = extraction_config or {}

        # Get document text
        text = ' '.join([page.text_content for page in document.pages.all()])

        # Use AI to extract data
        result = AIService.extract_data(text, extraction_type, extraction_config)

        # Save extraction
        DocumentExtraction.objects.create(
            document=document,
            extraction_type=extraction_type,
            structured_data=result.get('data', {}),
            confidence_score=result.get('confidence', 0.0),
            metadata=result.get('metadata', {})
        )

        logger.info(f'Document extraction completed: {document_id}')

    except Exception as e:
        logger.error(f'Document extraction failed: {str(e)}')
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_document_embeddings(self, document_id):
    """
    Generate embeddings for document text.

    Args:
        document_id: Document ID
    """
    try:
        from .models import Document, DocumentEmbedding
        from apps.ai_engine.services import AIService

        document = Document.objects.get(id=document_id)

        # Get all pages text
        pages = document.pages.all()

        for page in pages:
            # Split text into chunks (max 500 words per chunk)
            chunks = AIService.chunk_text(page.text_content, max_words=500)

            for idx, chunk in enumerate(chunks):
                # Generate embedding
                embedding = AIService.generate_embedding(chunk)

                DocumentEmbedding.objects.create(
                    document=document,
                    chunk_index=idx,
                    chunk_text=chunk,
                    embedding=embedding,
                    embedding_model='text-embedding-ada-002',  # Or configured model
                    metadata={'page': page.page_number}
                )

        logger.info(f'Document embeddings generated: {document_id}')

    except Exception as e:
        logger.error(f'Embedding generation failed: {str(e)}')
        raise self.retry(exc=e, countdown=60)
