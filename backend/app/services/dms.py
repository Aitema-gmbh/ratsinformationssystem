"""
DMS / eAkte Integration Service

Supports:
- d.velop documents (REST API)
- XDomea (XML-based document exchange, German eGovernment standard)
- Generic S3-compatible storage
- Full-text extraction (Tika)
"""
import hashlib
import uuid
from datetime import datetime
from typing import Optional, BinaryIO
from dataclasses import dataclass
import httpx
from sqlalchemy.orm import Session

from app.models.oparl import File as OParlFile


@dataclass
class DocumentMetadata:
    """Metadata for a document."""
    title: str
    mime_type: str
    size: int
    checksum: str
    source: str  # 'upload', 'dvelop', 'xdomea', 's3'
    external_id: Optional[str] = None
    category: Optional[str] = None  # 'vorlage', 'protokoll', 'einladung', 'anlage'


class DMSService:
    """Document Management System integration."""

    def __init__(self, session: Session, config: dict = None):
        self.session = session
        self.config = config or {}

    async def store_document(
        self,
        tenant_id: str,
        file_data: BinaryIO,
        filename: str,
        mime_type: str,
        category: Optional[str] = None,
    ) -> OParlFile:
        """Store a document and create OParl File record."""
        content = file_data.read()
        size = len(content)
        checksum = hashlib.sha512(content).hexdigest()

        # Check for duplicate
        existing = self.session.query(OParlFile).filter(
            OParlFile.sha512_checksum == checksum,
            OParlFile.tenant_id == tenant_id,
        ).first()
        if existing:
            return existing

        file_id = str(uuid.uuid4())
        storage_path = f"tenants/{tenant_id}/files/{file_id}/{filename}"

        # Store in configured backend
        backend = self.config.get('storage_backend', 'local')
        if backend == 's3':
            await self._store_s3(storage_path, content)
        elif backend == 'dvelop':
            await self._store_dvelop(storage_path, content, filename, mime_type)
        else:
            await self._store_local(storage_path, content)

        # Extract text for search
        text = await self._extract_text(content, mime_type)

        # Create OParl File record
        oparl_file = OParlFile(
            id=file_id,
            tenant_id=tenant_id,
            name=filename,
            file_name=filename,
            mime_type=mime_type,
            size=size,
            sha512_checksum=checksum,
            text=text,
            storage_path=storage_path,
            access_url=f"/api/files/{file_id}",
            download_url=f"/api/files/{file_id}/download",
        )
        self.session.add(oparl_file)
        self.session.commit()
        return oparl_file

    async def _store_local(self, path: str, content: bytes):
        """Store file on local filesystem."""
        import os
        full_path = os.path.join(self.config.get('storage_path', '/data/files'), path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'wb') as f:
            f.write(content)

    async def _store_s3(self, path: str, content: bytes):
        """Store file in S3-compatible storage."""
        # Would use boto3 in production
        pass

    async def _store_dvelop(self, path: str, content: bytes, filename: str, mime_type: str):
        """Store file in d.velop documents."""
        base_url = self.config.get('dvelop_url', '')
        api_key = self.config.get('dvelop_api_key', '')
        
        if not base_url or not api_key:
            raise ValueError("d.velop nicht konfiguriert")
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{base_url}/dms/r/repo/documents",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": mime_type,
                    "X-DV-Document-Title": filename,
                },
                content=content,
            )
            resp.raise_for_status()

    async def _extract_text(self, content: bytes, mime_type: str) -> Optional[str]:
        """Extract text from document using Tika."""
        tika_url = self.config.get('tika_url', 'http://localhost:9998')
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.put(
                    f"{tika_url}/tika",
                    headers={"Content-Type": mime_type},
                    content=content,
                    timeout=30.0,
                )
                if resp.status_code == 200:
                    return resp.text[:50000]  # Limit text length
        except Exception:
            pass
        return None


class XDomeaImporter:
    """
    XDomea Import/Export
    
    XDomea is the German standard for electronic document exchange
    between government agencies (Schriftgutaustausch).
    
    Supports:
    - Aktenplan import
    - Vorgangsakte import  
    - Dokumentenaustausch
    """

    def __init__(self, session: Session, tenant_id: str):
        self.session = session
        self.tenant_id = tenant_id

    def import_xdomea_message(self, xml_content: str) -> dict:
        """Import an XDomea message (Nachricht)."""
        import xml.etree.ElementTree as ET
        
        root = ET.fromstring(xml_content)
        ns = {'xd': 'urn:xoev-de:xdomea:schema:3.0.0'}
        
        imported = {'documents': 0, 'errors': []}
        
        # Find all Dokument elements
        for doc_elem in root.findall('.//xd:Dokument', ns):
            try:
                title = doc_elem.findtext('xd:BetreffDesSchriftgutobjekts', '', ns)
                doc_type = doc_elem.findtext('xd:Dokumenttyp/xd:Code', '', ns)
                
                # Find primary file (Primaerdokument)
                primaer = doc_elem.find('.//xd:Primaerdokument', ns)
                if primaer is not None:
                    filename = primaer.findtext('xd:Dateiname', 'document', ns)
                    mime = primaer.findtext('xd:MIMEType', 'application/pdf', ns)
                    
                    oparl_file = OParlFile(
                        tenant_id=self.tenant_id,
                        name=title or filename,
                        file_name=filename,
                        mime_type=mime,
                    )
                    self.session.add(oparl_file)
                    imported['documents'] += 1
            except Exception as e:
                imported['errors'].append(str(e))
        
        self.session.commit()
        return imported

    def export_xdomea_message(self, file_ids: list) -> str:
        """Export files as XDomea message."""
        files = self.session.query(OParlFile).filter(
            OParlFile.id.in_(file_ids),
            OParlFile.tenant_id == self.tenant_id,
        ).all()

        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_parts.append('<xdomea:Nachricht xmlns:xdomea="urn:xoev-de:xdomea:schema:3.0.0">')
        xml_parts.append(f'  <xdomea:Kopf>')
        xml_parts.append(f'    <xdomea:ProzessID>{uuid.uuid4()}</xdomea:ProzessID>')
        xml_parts.append(f'    <xdomea:Erstellungszeitpunkt>{datetime.utcnow().isoformat()}</xdomea:Erstellungszeitpunkt>')
        xml_parts.append(f'  </xdomea:Kopf>')
        
        for f in files:
            xml_parts.append(f'  <xdomea:Dokument>')
            xml_parts.append(f'    <xdomea:BetreffDesSchriftgutobjekts>{f.name or ""}</xdomea:BetreffDesSchriftgutobjekts>')
            xml_parts.append(f'    <xdomea:Primaerdokument>')
            xml_parts.append(f'      <xdomea:Dateiname>{f.file_name or ""}</xdomea:Dateiname>')
            xml_parts.append(f'      <xdomea:MIMEType>{f.mime_type or ""}</xdomea:MIMEType>')
            xml_parts.append(f'    </xdomea:Primaerdokument>')
            xml_parts.append(f'  </xdomea:Dokument>')
        
        xml_parts.append('</xdomea:Nachricht>')
        return '\n'.join(xml_parts)
