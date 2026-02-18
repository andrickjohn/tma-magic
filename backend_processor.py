#!/usr/bin/env python3
# Backend Processor - The "Brain"
"""
Standalone extraction script that runs as a subprocess.
Reads job JSON, processes file, writes status JSON.
Completely decoupled from the Streamlit UI.

Usage:
    python backend_processor.py <job_file.json>
    python backend_processor.py --test <file_path>
"""

import argparse
import json
import sys
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config, get_temp_dir
from engines.regex_engine import RegexEngine, FinancialData
from engines.ai_engine import AIEngine
from utils.pdf_parser import (
    extract_text_from_pdf,
    convert_pdf_to_images,
    extract_text_from_excel,
    detect_file_type
)


def update_status(
    status_file: Path,
    state: str,
    progress: float,
    message: str,
    data: Optional[Dict] = None,
    cost: float = 0.0,
    start_time: Optional[datetime] = None
):
    """Write status update for UI polling."""
    # Calculate ETA based on progress and elapsed time
    eta = 0
    if start_time and progress > 0.05:  # Only estimate after 5% progress
        elapsed = (datetime.now() - start_time).total_seconds()
        estimated_total = elapsed / progress
        eta = max(0, int(estimated_total - elapsed))
    
    status = {
        "state": state,
        "progress": progress,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "cost": cost,
        "eta": eta,
        "data": data
    }
    status_file.write_text(json.dumps(status, indent=2))


def process_file(
    file_path: Path,
    mode: str = "hybrid",
    confidence_threshold: int = 85,
    api_key: Optional[str] = None,
    status_file: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Main extraction logic.
    
    Args:
        file_path: Path to PDF or Excel file
        mode: "regex_only", "ai_only", or "hybrid"
        confidence_threshold: Threshold for falling back to AI
        api_key: OpenAI API key (required for AI mode)
        status_file: Optional path to write status updates
    
    Returns:
        Dict with extraction results
    """
    # Track cost and timing
    start_time = datetime.now()
    total_cost = 0.0
    
    def log(msg: str, progress: float = 0, cost: float = 0.0):
        nonlocal total_cost
        total_cost += cost
        if status_file:
            update_status(status_file, "processing", progress, msg, cost=total_cost, start_time=start_time)
        print(f"[{progress:.0%}] {msg}")
    
    
    # 1. Initialization
    log("Initializing extraction engine...", 0.05)
    
    # IMMEDIATE API KEY CHECK: Don't even try to read files if we need AI but have no key
    is_ai_mode = mode in ["ai_only", "hybrid"]
    if is_ai_mode and not api_key:
        # We allow Hybrid to try Regex first, but we want to warn early
        log("⚠️ No API Key! AI features disabled.", 0.05)
        if mode == "ai_only":
            raise ValueError("API KEY REQUIRED: Please enter your OpenAI key to use AI Extraction.")

    # Detect file type
    try:
        file_type = detect_file_type(file_path)
    except Exception as e:
        raise ValueError(f"File identification failed: {str(e)}")

    if file_type == "unknown":
        raise ValueError(f"Unsupported file type: {file_path.suffix}")
    
    log(f"Detected file type: {file_type.upper()}", 0.10)
    
    # Extract text/Prepare
    if file_type == "pdf":
        log("Reading PDF structure...", 0.15)
        text, is_digital = extract_text_from_pdf(file_path)
        if is_digital:
            log("Digital text extracted successfully.", 0.20)
        else:
            log("Scanned PDF detected. Preparing visual analysis...", 0.20)
            
    elif file_type == "excel":
        log("Parsing Excel workbook...", 0.15)
        text = extract_text_from_excel(file_path)
        is_digital = True
    else:
        text = ""
        is_digital = False
    
    results = []
    confidence = 0
    extraction_method = "none"
    
    # 2. Regex Extraction
    if mode != "ai_only" and is_digital and text:
        log("Running pattern matching algorithms...", 0.25)
        regex_engine = RegexEngine()
        results, confidence = regex_engine.extract(text, file_path.name)
        extraction_method = "regex"
        log(f"Pattern matching complete. Confidence: {confidence}%", 0.35)
    
    # 3. Decision Logic
    use_ai = (
        mode == "ai_only" or
        (mode == "hybrid" and confidence < confidence_threshold)
    )
    
    # Log if regex was sufficient (no AI cost)
    if not use_ai and mode == "hybrid":
        log(f"Regex extraction successful (confidence: {confidence}%) - No AI cost!", 0.40)
    
    # 4. AI Extraction
    if use_ai:
        if not api_key:
            log("⚠️ AI Analysis Required But API Key Missing.", 0.40)
            if not results:
                raise ValueError("API KEY REQUIRED: Visual analysis is needed for this document but no key was provided.")
        else:
            log("Starting AI visual analysis...", 0.40)
            if file_type == "pdf":
                log("converting PDF pages to high-res images...", 0.45)
                image_paths = convert_pdf_to_images(file_path)
                
                total_pages = len(image_paths)
                log(f"Analyzing {total_pages} page(s) with AI models...", 0.50)
                
                # Note: We could iterate here for granular page progress if AIEngine supported it
                # For now, we jump to 80% after AI is done since it's the longest step
                ai_engine = AIEngine(api_key)
                ai_results, ai_confidence, ai_cost = ai_engine.extract_from_pdf_pages(image_paths)
                
                log("AI analysis complete. Consolidating data...", 0.85, cost=ai_cost)
                
                if ai_confidence > confidence:
                    results = ai_results
                    confidence = ai_confidence
                    extraction_method = "ai"
                elif results:
                    extraction_method = "hybrid"
                
                log(f"Final Confidence: {ai_confidence}%", 0.90)
    
    log("Formatting final report...", 0.95)
    
    # Format output
    output = {
        "success": True,
        "file": str(file_path.name),
        "extraction_method": extraction_method,
        "confidence": confidence,
        "years": [r.to_dict() for r in results],
        "processed_at": datetime.now().isoformat(),
        "total_cost": total_cost
    }
    
    log("Extraction complete!", 1.0)
    return output


def main():
    parser = argparse.ArgumentParser(description="TMA Magic Black Box - Backend Processor")
    parser.add_argument("job_file", nargs="?", help="Path to job JSON file")
    parser.add_argument("--test", help="Test mode: process a single file")
    parser.add_argument("--mode", default="hybrid", choices=["regex_only", "ai_only", "hybrid"])
    args = parser.parse_args()
    
    config = get_config()
    
    if args.test:
        # Test mode: direct file processing
        file_path = Path(args.test)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            sys.exit(1)
        
        try:
            result = process_file(
                file_path,
                mode=args.mode,
                confidence_threshold=config.confidence_threshold,
                api_key=config.openai_api_key
            )
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            sys.exit(1)
    
    elif args.job_file:
        # Job mode: read from JSON, write status
        job_file = Path(args.job_file)
        if not job_file.exists():
            print(f"Error: Job file not found: {job_file}")
            sys.exit(1)
        
        job = json.loads(job_file.read_text())
        job_id = job.get("job_id", "unknown")
        status_file = get_temp_dir() / f"tma_status_{job_id}.json"
        
        try:
            result = process_file(
                Path(job["file_path"]),
                mode=job.get("mode", "hybrid"),
                confidence_threshold=job.get("confidence_threshold", config.confidence_threshold),
                api_key=job.get("api_key") or config.openai_api_key,
                status_file=status_file
            )
            update_status(status_file, "complete", 1.0, "Done", result, cost=result.get("total_cost", 0.0))
        
        except Exception as e:
            update_status(status_file, "error", 0, str(e))
            traceback.print_exc()
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
