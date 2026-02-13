# AI-based Financial Data Extraction Engine
"""
GPT-4o Vision fallback for scanned documents and complex tables.
Used when Regex confidence is below threshold.
"""

import base64
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.regex_engine import FinancialData, ExtractionResult


class AIEngine:
    """OpenAI GPT-4o Vision based extractor."""
    
    EXTRACTION_PROMPT = """You are a financial data extraction expert. Analyze this document image and extract the following data points for each year present (2022, 2023, 2024 if available):

**Income Statement:**
- Revenue (Total Sales/Net Sales)
- Net Income (Net Profit)  
- Depreciation

**Balance Sheet:**
- Total Assets
- Total Liabilities

**Cash Flow / Debt:**
- Total CPLTD (Current Portion of Long-Term Debt)

Return your response as valid JSON in this exact format:
{
    "years": [
        {
            "year": 2024,
            "revenue": 19297,
            "net_income": 92,
            "depreciation": 555,
            "assets": 10320,
            "liabilities": 9041,
            "total_cpltd": 4845
        }
    ],
    "confidence": 90,
    "notes": "Any relevant observations"
}

Rules:
- Use null for fields you cannot find
- Numbers should be raw values (no $ or commas)
- Negative values for losses (e.g., -122 not ($122))
- Confidence is your estimate 0-100 of extraction accuracy
"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None
    
    @property
    def client(self):
        """Lazy-load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        return self._client
    
    def encode_image(self, image_path: Path) -> str:
        """Encode image to base64 for API."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def extract_from_image(self, image_path: Path) -> Tuple[List[FinancialData], int]:
        """Extract financial data from a single image."""
        base64_image = self.encode_image(image_path)
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.EXTRACTION_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        return self._parse_response(response.choices[0].message.content)
    
    def extract_from_pdf_pages(self, image_paths: List[Path]) -> Tuple[List[FinancialData], int]:
        """Extract from multiple PDF page images."""
        all_results: Dict[int, FinancialData] = {}
        total_confidence = 0
        
        for image_path in image_paths:
            try:
                results, confidence = self.extract_from_image(image_path)
                total_confidence += confidence
                
                for data in results:
                    if data.year not in all_results:
                        all_results[data.year] = data
                    else:
                        # Merge: prefer higher confidence values
                        existing = all_results[data.year]
                        self._merge_data(existing, data)
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                continue
        
        avg_confidence = total_confidence // max(len(image_paths), 1)
        return list(all_results.values()), avg_confidence
    
    def _merge_data(self, existing: FinancialData, new: FinancialData):
        """Merge new data into existing, preferring higher confidence."""
        for field in ["revenue", "net_income", "depreciation", "assets", "liabilities", "total_cpltd"]:
            existing_val = getattr(existing, field)
            new_val = getattr(new, field)
            if new_val.confidence > existing_val.confidence:
                setattr(existing, field, new_val)
    
    def _parse_response(self, content: str) -> Tuple[List[FinancialData], int]:
        """Parse AI response into FinancialData objects."""
        # Extract JSON from response (may be wrapped in markdown)
        json_match = content
        if "```json" in content:
            json_match = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            json_match = content.split("```")[1].split("```")[0]
        
        try:
            data = json.loads(json_match.strip())
        except json.JSONDecodeError:
            return [], 0
        
        results = []
        confidence = data.get("confidence", 75)
        
        for year_data in data.get("years", []):
            fd = FinancialData(year=year_data.get("year", 0))
            
            for field in ["revenue", "net_income", "depreciation", "assets", "liabilities", "total_cpltd"]:
                value = year_data.get(field)
                if value is not None:
                    setattr(fd, field, ExtractionResult(
                        value=float(value),
                        confidence=confidence,
                        raw_text=str(value)
                    ))
            
            results.append(fd)
        
        return results, confidence
