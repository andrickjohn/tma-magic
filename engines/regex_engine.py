# Regex-based Financial Data Extraction Engine
"""
Pattern-based extraction for digital PDFs.
Zero-cost, instant extraction with confidence scoring.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ExtractionResult:
    """Result from extraction with confidence."""
    value: Optional[float] = None
    raw_text: str = ""
    confidence: int = 0  # 0-100
    source_line: str = ""


@dataclass 
class FinancialData:
    """Structured financial data for a single year."""
    year: int = 0
    revenue: ExtractionResult = field(default_factory=ExtractionResult)
    net_income: ExtractionResult = field(default_factory=ExtractionResult)
    depreciation: ExtractionResult = field(default_factory=ExtractionResult)
    assets: ExtractionResult = field(default_factory=ExtractionResult)
    liabilities: ExtractionResult = field(default_factory=ExtractionResult)
    total_cpltd: ExtractionResult = field(default_factory=ExtractionResult)
    
    def overall_confidence(self) -> int:
        """Average confidence across all fields."""
        fields = [
            self.revenue, self.net_income, self.depreciation,
            self.assets, self.liabilities, self.total_cpltd
        ]
        filled = [f for f in fields if f.value is not None]
        if not filled:
            return 0
        return sum(f.confidence for f in filled) // len(filled)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "year": self.year,
            "revenue": self.revenue.value,
            "net_income": self.net_income.value,
            "depreciation": self.depreciation.value,
            "assets": self.assets.value,
            "liabilities": self.liabilities.value,
            "total_cpltd": self.total_cpltd.value,
            "confidence": self.overall_confidence()
        }


class RegexEngine:
    """Regex-based financial data extractor."""
    
    # Common patterns for financial values
    MONEY_PATTERN = r'\$?\s*[\d,]+(?:\.\d{2})?|\([\d,]+(?:\.\d{2})?\)'
    YEAR_PATTERN = r'20\d{2}'
    
    # Field-specific patterns (label followed by value)
    # QuickBooks formats: "TOTAL ASSETS $6,411,348.49" or "Total Income $13,325,650.63"
    PATTERNS = {
        "revenue": [
            r'Total\s+Income\s+\$([\d,]+(?:\.\d{2})?)',
            r'GROSS\s+PROFIT\s+\$([\d,]+(?:\.\d{2})?)',
            r'(?:total\s+)?(?:net\s+)?(?:sales|revenue)\s+\$([\d,]+(?:\.\d{2})?)',
            r'gross\s+(?:sales|revenue)\s+\$([\d,]+(?:\.\d{2})?)',
        ],
        "net_income": [
            r'net\s+(?:income|profit|earnings?)\s+\$?([\d,]+(?:\.\d{2})?)',
            r'net\s+(?:income|profit)\s+\(?([\d,]+(?:\.\d{2})?)\)?',
            r'(?:net\s+)?(?:ordinary\s+)?income\s+\$?([\d,]+(?:\.\d{2})?)',
        ],
        "depreciation": [
            r'depreciation(?:\s+(?:and|&)\s+amortization)?\s+\$?([\d,]+(?:\.\d{2})?)',
            r'(?:total\s+)?depreciation\s+\$?([\d,]+(?:\.\d{2})?)',
            r'accumulated\s+depreciation\s+\$?([\d,]+(?:\.\d{2})?)',
        ],
        "assets": [
            r'total\s+assets\s+\$?([\d,]+(?:\.\d{2})?)',
            r'assets[\s,]+total\s+\$?([\d,]+(?:\.\d{2})?)',
            r'TOTAL\s+ASSETS\s+\$?([\d,]+(?:\.\d{2})?)',
        ],
        "liabilities": [
            r'total\s+liabilities\s+\$?([\d,]+(?:\.\d{2})?)',
            r'liabilities[\s,]+total\s+\$?([\d,]+(?:\.\d{2})?)',
            r'TOTAL\s+LIABILITIES\s+(?:AND\s+EQUITY\s+)?\$?([\d,]+(?:\.\d{2})?)',
        ],
        "total_cpltd": [
            r'long[\s-]?term\s+liabilities\s+\$?([\d,]+(?:\.\d{2})?)',
            r'(?:current\s+portion\s+(?:of\s+)?)?(?:long[\s-]?term\s+)?debt\s+\$?([\d,]+(?:\.\d{2})?)',
            r'cpltd\s+\$?([\d,]+(?:\.\d{2})?)',
            r'notes\s+payable\s+\$?([\d,]+(?:\.\d{2})?)',
        ],
    }
    
    def __init__(self):
        self.compiled_patterns = {}
        for field, patterns in self.PATTERNS.items():
            self.compiled_patterns[field] = [
                re.compile(p, re.IGNORECASE | re.MULTILINE)
                for p in patterns
            ]
    
    def parse_money(self, text: str) -> Optional[float]:
        """Parse a money string to float."""
        if not text:
            return None
        
        # Remove $ and spaces
        cleaned = text.replace('$', '').replace(' ', '').replace(',', '')
        
        # Handle parentheses as negative
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def extract_years(self, text: str, filename: str = "") -> List[int]:
        """Find fiscal years mentioned in the document (not print dates)."""
        from datetime import datetime
        current_year = datetime.now().year
        
        # Priority 0: Extract year from filename (e.g., "2024ProfitandLoss.pdf")
        filename_years = re.findall(r'(20\d{2})', filename)
        if filename_years:
            # Use filename year as the primary year
            return [int(filename_years[0])]
        
        # Priority 1: Look for "As of [date] YYYY" or "Year Ended YYYY" patterns
        fiscal_patterns = [
            r'[Aa]s\s+of\s+(?:\w+\s+\d{1,2},?\s+)?(20\d{2})',
            r'[Yy]ear\s+[Ee]nded\s+(?:\w+\s+\d{1,2},?\s+)?(20\d{2})',
            r'[Ff]or\s+(?:the\s+)?[Yy]ear\s+(20\d{2})',
            r'[Ff]iscal\s+[Yy]ear\s+(20\d{2})',
            r'FY\s*(20\d{2})',
        ]
        
        fiscal_years = []
        for pattern in fiscal_patterns:
            matches = re.findall(pattern, text)
            for y in matches:
                yr = int(y)
                # Only accept years that are not in the future
                if 2000 <= yr <= current_year:
                    fiscal_years.append(yr)
        
        if fiscal_years:
            # Return unique fiscal years, sorted descending, max 3
            return sorted(set(fiscal_years), reverse=True)[:3]
        
        # Fallback: Find all years but STRICTLY filter
        # - Exclude future years (print dates like 2025)
        # - Exclude very old years (pre-2015)
        all_matches = re.findall(self.YEAR_PATTERN, text)
        years = []
        for y in all_matches:
            yr = int(y)
            if 2015 <= yr <= current_year:  # Only past/present years
                years.append(yr)
        
        years = sorted(set(years), reverse=True)
        return years[:3]  # Max 3 most recent years
    
    def extract_field(self, text: str, field: str) -> ExtractionResult:
        """Extract a single field from text."""
        patterns = self.compiled_patterns.get(field, [])
        
        for i, pattern in enumerate(patterns):
            match = pattern.search(text)
            if match:
                raw = match.group(1)
                value = self.parse_money(raw)
                if value is not None:
                    # Higher confidence for earlier patterns (more specific)
                    confidence = 95 - (i * 10)
                    return ExtractionResult(
                        value=value,
                        raw_text=raw,
                        confidence=max(confidence, 60),
                        source_line=match.group(0)[:100]
                    )
        
        return ExtractionResult(confidence=0)
    
    def extract(self, text: str, filename: str = "") -> Tuple[List[FinancialData], int]:
        """
        Extract financial data from text.
        Returns list of FinancialData (one per year) and overall confidence.
        """
        years = self.extract_years(text, filename)
        if not years:
            from datetime import datetime
            years = [datetime.now().year]  # Default to current year
        
        results = []
        seen_data_signatures = set()  # Track unique data to avoid duplicates
        
        for year in years:
            data = FinancialData(year=year)
            
            # Try to find year-specific sections
            year_text = self._find_year_section(text, year)
            search_text = year_text if year_text else text
            
            data.revenue = self.extract_field(search_text, "revenue")
            data.net_income = self.extract_field(search_text, "net_income")
            data.depreciation = self.extract_field(search_text, "depreciation")
            data.assets = self.extract_field(search_text, "assets")
            data.liabilities = self.extract_field(search_text, "liabilities")
            data.total_cpltd = self.extract_field(search_text, "total_cpltd")
            
            # Create a signature of the data values to detect duplicates
            data_sig = (
                data.revenue.value, data.net_income.value, data.depreciation.value,
                data.assets.value, data.liabilities.value, data.total_cpltd.value
            )
            
            # Only add if this is unique data OR all values are None
            if data_sig not in seen_data_signatures:
                seen_data_signatures.add(data_sig)
                results.append(data)
        
        # If we have duplicate data, keep only the first (most recent) year
        overall_confidence = sum(r.overall_confidence() for r in results) // max(len(results), 1)
        return results, overall_confidence
    
    def _find_year_section(self, text: str, year: int) -> Optional[str]:
        """Try to isolate text specific to a year."""
        # Look for sections starting with the year
        pattern = rf'{year}[\s\S]{{100,2000}}?(?=20\d{{2}}|$)'
        match = re.search(pattern, text)
        return match.group(0) if match else None
