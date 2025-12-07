"""
Data Ingestion Module
Handles loading and preprocessing of raw data
"""

import json
from typing import List, Dict, Any
from pathlib import Path
from langchain_core.documents import Document
import pandas as pd
from src.utils import get_logger


logger = get_logger(__name__)


class DataLoader:
    """Loads data from various sources (JSON, CSV, etc.)"""
    
    def __init__(self):
        """Initialize the data loader"""
        self.logger = logger
    
    def load_json(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load JSON file containing pond data
        
        Args:
            file_path: Path to JSON file
        
        Returns:
            List of data records
        """
        try:
            self.logger.info(f"Loading JSON file: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both direct lists and nested 'data' key
            records = data.get('data', data) if isinstance(data, dict) else data
            
            if not isinstance(records, list):
                raise ValueError("Expected JSON to contain a list of records")
            
            self.logger.info(f"Successfully loaded {len(records)} records from JSON")
            return records
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading JSON file: {e}")
            raise
    
    def load_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load CSV file
        
        Args:
            file_path: Path to CSV file
        
        Returns:
            List of data records as dictionaries
        """
        try:
            self.logger.info(f"Loading CSV file: {file_path}")
            
            df = pd.read_csv(file_path)
            records = df.to_dict('records')
            
            self.logger.info(f"Successfully loaded {len(records)} records from CSV")
            return records
        
        except Exception as e:
            self.logger.error(f"Error loading CSV file: {e}")
            raise


class DataPreprocessor:
    """Preprocesses and cleans raw data"""
    
    def __init__(self):
        """Initialize the preprocessor"""
        self.logger = logger
    
    def preprocess_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Preprocess raw records
        
        Args:
            records: List of raw records
        
        Returns:
            List of preprocessed records
        """
        self.logger.info(f"Preprocessing {len(records)} records")
        
        preprocessed = []
        for i, record in enumerate(records):
            try:
                cleaned_record = self._clean_record(record)
                preprocessed.append(cleaned_record)
            except Exception as e:
                self.logger.warning(f"Error preprocessing record {i}: {e}")
                continue
        
        self.logger.info(f"Successfully preprocessed {len(preprocessed)} records")
        return preprocessed
    
    @staticmethod
    def _clean_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean a single record
        
        Args:
            record: Single data record
        
        Returns:
            Cleaned record
        """
        cleaned = {}
        
        for key, value in record.items():
            # Remove extra whitespace from keys
            clean_key = key.strip()
            
            # Handle None and empty values
            if value is None:
                cleaned[clean_key] = "N/A"
            elif isinstance(value, str):
                cleaned[clean_key] = value.strip()
            elif isinstance(value, (int, float)):
                cleaned[clean_key] = value
            else:
                cleaned[clean_key] = str(value)
        
        return cleaned
    
    def convert_to_documents(
        self, 
        records: List[Dict[str, Any]], 
        source: str = "pond_data"
    ) -> List[Document]:
        """
        Convert records to LangChain Document objects
        
        Args:
            records: List of preprocessed records
            source: Source identifier for metadata
        
        Returns:
            List of LangChain Document objects
        """
        self.logger.info(f"Converting {len(records)} records to Documents")
        
        documents = []
        for i, record in enumerate(records):
            # Create formatted text content from record
            content = self._format_record_as_text(record)
            
            # Create metadata
            metadata = {
                "source": source,
                "record_index": i,
                "pond": record.get("Pond", "Unknown"),
                "crop_id": record.get("Crop ID", "Unknown"),
                "status": record.get("status", "Unknown"),
            }
            
            # Create Document
            doc = Document(page_content=content, metadata=metadata)
            documents.append(doc)
        
        self.logger.info(f"Created {len(documents)} documents")
        return documents
    
    @staticmethod
    def _format_record_as_text(record: Dict[str, Any]) -> str:
        """
        Format a record as readable text
        
        Args:
            record: Single record dictionary
        
        Returns:
            Formatted text representation
        """
        lines = []
        
        # Add key information first
        pond = record.get("Pond", "Unknown")
        crop_id = record.get("Crop ID", "Unknown")
        status = record.get("status", "Unknown")
        
        lines.append(f"Pond: {pond}")
        lines.append(f"Crop ID: {crop_id}")
        lines.append(f"Status: {status}")
        lines.append("")
        
        # Add all other fields
        skip_keys = {"Pond", "Crop ID", "status"}
        for key, value in record.items():
            if key not in skip_keys:
                lines.append(f"{key}: {value}")
        
        return "\n".join(lines)
