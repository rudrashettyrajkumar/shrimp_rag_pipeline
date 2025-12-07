"""
Utility functions for text processing and helpers
"""

import json
import re
from typing import List, Dict, Any, Tuple
import hashlib


class TextProcessor:
    """Utility class for text processing operations"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Input text
        
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep alphanumeric and basic punctuation
        text = re.sub(r'[^\w\s.,;:!?\-()]', '', text)
        
        return text.strip()
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 500) -> str:
        """
        Truncate text to maximum length
        
        Args:
            text: Input text
            max_length: Maximum length
        
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    @staticmethod
    def get_text_hash(text: str) -> str:
        """
        Get MD5 hash of text
        
        Args:
            text: Input text
        
        Returns:
            MD5 hash string
        """
        return hashlib.md5(text.encode()).hexdigest()


class DataProcessor:
    """Utility class for data processing operations"""
    
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """
        Load JSON file
        
        Args:
            file_path: Path to JSON file
        
        Returns:
            Parsed JSON content
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: str, indent: int = 2):
        """
        Save data to JSON file
        
        Args:
            data: Data to save
            file_path: Path to save file
            indent: JSON indentation level
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """
        Flatten nested dictionary
        
        Args:
            d: Dictionary to flatten
            parent_key: Parent key prefix
            sep: Separator for nested keys
        
        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(
                    DataProcessor.flatten_dict(v, new_key, sep=sep).items()
                )
            else:
                items.append((new_key, v))
        return dict(items)
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """
        Extract all numbers from text
        
        Args:
            text: Input text
        
        Returns:
            List of extracted numbers
        """
        pattern = r'-?\d+\.?\d*'
        return [float(x) for x in re.findall(pattern, text)]


class MetricsCalculator:
    """Utility class for calculating metrics"""
    
    @staticmethod
    def calculate_survival_percentage(initial_count: int, final_count: int) -> float:
        """
        Calculate survival percentage
        
        Args:
            initial_count: Initial stocking count
            final_count: Final count
        
        Returns:
            Survival percentage
        """
        if initial_count == 0:
            return 0.0
        return (final_count / initial_count) * 100
    
    @staticmethod
    def calculate_average(values: List[float]) -> float:
        """
        Calculate average of values
        
        Args:
            values: List of numbers
        
        Returns:
            Average value
        """
        if not values:
            return 0.0
        return sum(values) / len(values)
    
    @staticmethod
    def calculate_growth_rate(start_weight: float, end_weight: float, days: int) -> float:
        """
        Calculate daily growth rate
        
        Args:
            start_weight: Starting weight
            end_weight: Ending weight
            days: Number of days
        
        Returns:
            Daily growth rate in grams/day
        """
        if days == 0:
            return 0.0
        return (end_weight - start_weight) / days
