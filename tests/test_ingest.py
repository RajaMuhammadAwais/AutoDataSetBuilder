"""
Unit tests for autods.ingest module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import uuid
import hashlib
import io
import sys
from pathlib import Path

# Add SDK to path
sys.path.insert(0, str(Path(__file__).parent.parent / "sdk"))

from autods.ingest import IngestClient


class TestIngestClient(unittest.TestCase):
    """Test cases for IngestClient class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.s3_bucket = "test-bucket"
        self.db_url = "postgresql://user:pass@localhost/db"
    
    @patch('autods.ingest.boto3.client')
    @patch('autods.ingest.psycopg2.connect')
    def test_init_success(self, mock_db_connect, mock_s3_client):
        """Test successful initialization"""
        mock_db_connect.return_value = MagicMock()
        
        client = IngestClient(
            s3_bucket=self.s3_bucket,
            db_url=self.db_url
        )
        
        self.assertEqual(client.bucket, self.s3_bucket)
        mock_db_connect.assert_called_once()
    
    @patch('autods.ingest.psycopg2.connect')
    def test_init_db_connection_error(self, mock_db_connect):
        """Test initialization with database connection error"""
        import psycopg2
        mock_db_connect.side_effect = psycopg2.OperationalError("Connection failed")
        
        with self.assertRaises(psycopg2.OperationalError):
            IngestClient(s3_bucket=self.s3_bucket, db_url=self.db_url)
    
    @patch('autods.ingest.requests.get')
    @patch('autods.ingest.boto3.client')
    @patch('autods.ingest.psycopg2.connect')
    def test_ingest_url_success(self, mock_db_connect, mock_s3_client, mock_requests_get):
        """Test successful URL ingestion"""
        # Setup mocks
        test_content = b"test image data"
        mock_response = MagicMock()
        mock_response.content = test_content
        mock_requests_get.return_value = mock_response
        
        mock_conn = MagicMock()
        mock_db_connect.return_value = mock_conn
        
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        
        # Create client
        client = IngestClient(
            s3_bucket=self.s3_bucket,
            db_url=self.db_url
        )
        
        # Test ingestion
        test_url = "https://example.com/image.jpg"
        result = client.ingest_url(test_url, license="cc0", source="test")
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertIn('id', result)
        self.assertIn('s3_key', result)
        self.assertIn('checksum', result)
        
        # Verify S3 put was called
        mock_s3.put_object.assert_called_once()
    
    @patch('autods.ingest.requests.get')
    @patch('autods.ingest.boto3.client')
    @patch('autods.ingest.psycopg2.connect')
    def test_ingest_url_download_failure(self, mock_db_connect, mock_s3_client, mock_requests_get):
        """Test ingestion with download failure"""
        import requests
        
        mock_requests_get.side_effect = requests.ConnectionError("Network error")
        mock_db_connect.return_value = MagicMock()
        mock_s3_client.return_value = MagicMock()
        
        client = IngestClient(
            s3_bucket=self.s3_bucket,
            db_url=self.db_url
        )
        
        result = client.ingest_url("https://invalid.example.com/image.jpg")
        self.assertIsNone(result)
    
    @patch('autods.ingest.hashlib.sha256')
    @patch('autods.ingest.requests.get')
    @patch('autods.ingest.boto3.client')
    @patch('autods.ingest.psycopg2.connect')
    def test_checksum_calculation(self, mock_db_connect, mock_s3_client, mock_requests_get, mock_sha256):
        """Test checksum calculation"""
        test_content = b"test data"
        mock_response = MagicMock()
        mock_response.content = test_content
        mock_requests_get.return_value = mock_response
        
        expected_hash = hashlib.sha256(test_content).hexdigest()
        mock_sha256.return_value.hexdigest.return_value = expected_hash
        
        mock_db_connect.return_value = MagicMock()
        mock_s3_client.return_value = MagicMock()
        
        client = IngestClient(
            s3_bucket=self.s3_bucket,
            db_url=self.db_url
        )
        
        result = client.ingest_url("https://example.com/file")
        
        self.assertEqual(result['checksum'], expected_hash)
    
    @patch('autods.ingest.boto3.client')
    @patch('autods.ingest.psycopg2.connect')
    def test_close(self, mock_db_connect, mock_s3_client):
        """Test connection cleanup"""
        mock_conn = MagicMock()
        mock_db_connect.return_value = mock_conn
        
        client = IngestClient(
            s3_bucket=self.s3_bucket,
            db_url=self.db_url
        )
        
        client.close()
        mock_conn.close.assert_called_once()

    @patch('autods.ingest.boto3.client')
    @patch('autods.ingest.psycopg2.connect')
    def test_close_with_s3(self, mock_db_connect, mock_s3_client):
        """Test that close() calls both DB and S3 client's close when present"""
        mock_conn = MagicMock()
        mock_db_connect.return_value = mock_conn

        mock_s3 = MagicMock()
        # Provide a close method on the mocked S3 client
        mock_s3.close = MagicMock()
        mock_s3_client.return_value = mock_s3

        client = IngestClient(
            s3_bucket=self.s3_bucket,
            db_url=self.db_url
        )

        client.close()
        mock_conn.close.assert_called_once()
        mock_s3.close.assert_called_once()


class TestIngestClientIntegration(unittest.TestCase):
    """Integration tests for IngestClient"""
    
    @patch('autods.ingest.requests.get')
    @patch('autods.ingest.boto3.client')
    @patch('autods.ingest.psycopg2.connect')
    def test_multiple_ingestions(self, mock_db_connect, mock_s3_client, mock_requests_get):
        """Test multiple sequential ingestions"""
        urls = [
            "https://example.com/img1.jpg",
            "https://example.com/img2.jpg",
            "https://example.com/img3.jpg",
        ]
        
        # Setup mocks for multiple responses
        mock_responses = []
        for i, url in enumerate(urls):
            mock_response = MagicMock()
            mock_response.content = f"test data {i}".encode()
            mock_responses.append(mock_response)
        
        mock_requests_get.side_effect = mock_responses
        mock_db_connect.return_value = MagicMock()
        mock_s3_client.return_value = MagicMock()
        
        client = IngestClient(
            s3_bucket="test-bucket",
            db_url="postgresql://user:pass@localhost/db"
        )
        
        results = []
        for url in urls:
            result = client.ingest_url(url, license="cc0", source="test")
            if result:
                results.append(result)
        
        self.assertEqual(len(results), len(urls))
        client.close()


if __name__ == '__main__':
    unittest.main()
