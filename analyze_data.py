"""
Data Analysis and Exploration Script
Analyzes the input data structure and provides insights
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ingestion import DataLoader


def analyze_data(file_path: str):
    """Analyze and display data structure and statistics"""
    
    print("\n" + "="*70)
    print("  DATA ANALYSIS REPORT")
    print("="*70)
    
    try:
        # Load data
        loader = DataLoader()
        records = loader.load_json(file_path)
        
        print(f"\n[1] Basic Statistics")
        print("-" * 70)
        print(f"Total Records: {len(records)}")
        
        # Analyze fields
        all_fields = set()
        field_types = defaultdict(set)
        
        for record in records:
            for key, value in record.items():
                all_fields.add(key)
                field_types[key].add(type(value).__name__)
        
        print(f"Total Unique Fields: {len(all_fields)}")
        
        # Field analysis
        print(f"\n[2] Field Structure")
        print("-" * 70)
        print(f"{'Field Name':<30} {'Type':<15} {'Sample Value'}")
        print("-" * 70)
        
        for field in sorted(all_fields):
            # Get type
            types = field_types[field]
            type_str = ", ".join(sorted(types))
            
            # Get sample value
            sample = records[0].get(field, "N/A")
            if isinstance(sample, str):
                sample = sample[:40]
            
            print(f"{field:<30} {type_str:<15} {sample}")
        
        # Categorical analysis
        print(f"\n[3] Categorical Fields Analysis")
        print("-" * 70)
        
        categorical_fields = {
            "Pond": "Pond Names",
            "status": "Crop Status",
            "spanningYear": "Spanning Years",
        }
        
        for field_key, field_label in categorical_fields.items():
            unique_values = set()
            for record in records:
                if field_key in record:
                    unique_values.add(str(record[field_key]))
            
            print(f"\n{field_label} ({field_key}):")
            for value in sorted(unique_values):
                count = sum(1 for r in records if str(r.get(field_key)) == value)
                print(f"  - {value}: {count} records")
        
        # Numerical analysis
        print(f"\n[4] Numerical Fields Analysis")
        print("-" * 70)
        
        numerical_fields = [
            "Stocking", "ABW", "FCR", "BM", "Survival",
            "DOC", "Week", "Weekly Inc", "Hectares"
        ]
        
        for field in numerical_fields:
            values = []
            for record in records:
                try:
                    val = float(record.get(field, 0))
                    if val > 0:
                        values.append(val)
                except (ValueError, TypeError):
                    pass
            
            if values:
                print(f"\n{field}:")
                print(f"  - Count: {len(values)}")
                print(f"  - Min: {min(values):.2f}")
                print(f"  - Max: {max(values):.2f}")
                print(f"  - Avg: {sum(values)/len(values):.2f}")
        
        # Sample record
        print(f"\n[5] Sample Record")
        print("-" * 70)
        print(json.dumps(records[0], indent=2))
        
        print("\n" + "="*70)
        print("✓ Data analysis complete")
        print("="*70 + "\n")
    
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")


if __name__ == "__main__":
    data_file = "./data/raw/pond_data.json"
    analyze_data(data_file)
