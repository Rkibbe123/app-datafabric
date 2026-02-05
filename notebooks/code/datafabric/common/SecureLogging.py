"""
SecureLogging - Secure error handling and logging for Databricks notebooks.
Prevents sensitive data leakage in logs and notebook outputs.

Usage:
    from common.SecureLogging import SecureLogger
    logger = SecureLogger(dbutils=dbutils)
    
    try:
        # your code
    except Exception as e:
        logger.log_error("process_name", e, task_id="123")
"""

import re
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any


class SecureLogger:
    """
    Secure logging utility that sanitizes error messages before output.
    Redacts common secret patterns and provides safe error logging.
    """
    
    # Patterns that indicate sensitive data - will be redacted
    REDACTION_PATTERNS = [
        # Connection strings
        (r'(password|pwd)\s*[=:]\s*[^\s;]+', r'\1=***REDACTED***'),
        (r'(server|host)\s*[=:]\s*[^\s;]+', r'\1=***REDACTED***'),
        (r'(user\s*id|uid|username)\s*[=:]\s*[^\s;]+', r'\1=***REDACTED***'),
        
        # API keys and tokens
        (r'(api[_-]?key|apikey)\s*[=:]\s*[^\s]+', r'\1=***REDACTED***'),
        (r'(bearer|token)\s+[a-zA-Z0-9\-_\.]+', r'\1 ***REDACTED***'),
        (r'(authorization)\s*[=:]\s*[^\s]+', r'\1=***REDACTED***'),
        
        # Azure/AWS patterns
        (r'(AccountKey|SharedAccessSignature)\s*[=:]\s*[^\s;]+', r'\1=***REDACTED***'),
        (r'DefaultEndpointsProtocol=https;[^"\']+', '***CONNECTION_STRING_REDACTED***'),
        (r'(aws[_-]?access[_-]?key[_-]?id|aws[_-]?secret)\s*[=:]\s*[^\s]+', r'\1=***REDACTED***'),
        
        # File paths that might expose infrastructure
        (r'/dbfs/mnt/[^\s]+', '/dbfs/mnt/***PATH_REDACTED***'),
        (r'abfss://[^\s]+', 'abfss://***STORAGE_REDACTED***'),
        
        # IP addresses
        (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '***IP_REDACTED***'),
        
        # Email addresses
        (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '***EMAIL_REDACTED***'),
    ]
    
    def __init__(self, dbutils=None, log_table: str = None, max_message_length: int = 500):
        """
        Initialize the secure logger.
        
        Args:
            dbutils: Databricks dbutils object (optional, for secret scope access)
            log_table: Delta table to store detailed logs (optional)
            max_message_length: Maximum length of error messages to display
        """
        self.dbutils = dbutils
        self.log_table = log_table
        self.max_message_length = max_message_length
        self._compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), replacement) 
            for pattern, replacement in self.REDACTION_PATTERNS
        ]
    
    def sanitize(self, text: str) -> str:
        """
        Remove sensitive information from text.
        
        Args:
            text: The text to sanitize
            
        Returns:
            Sanitized text with sensitive data redacted
        """
        if not text:
            return ""
        
        sanitized = str(text)
        for pattern, replacement in self._compiled_patterns:
            sanitized = pattern.sub(replacement, sanitized)
        
        # Truncate if too long
        if len(sanitized) > self.max_message_length:
            sanitized = sanitized[:self.max_message_length] + "... [truncated]"
        
        return sanitized
    
    def get_safe_exception_type(self, exception: Exception) -> str:
        """Get the exception type name safely."""
        return type(exception).__name__
    
    def get_error_hash(self, exception: Exception) -> str:
        """Generate a hash for error correlation without exposing details."""
        error_str = f"{type(exception).__name__}:{str(exception)[:100]}"
        return hashlib.sha256(error_str.encode()).hexdigest()[:12]
    
    def log_error(
        self, 
        process_name: str, 
        exception: Exception, 
        task_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        include_traceback: bool = False
    ) -> Dict[str, Any]:
        """
        Log an error safely without exposing sensitive information.
        
        Args:
            process_name: Name of the process/function that failed
            exception: The exception that was caught
            task_id: Optional task identifier for correlation
            context: Optional dict of additional context (will be sanitized)
            include_traceback: If True, stores full traceback in secure location
            
        Returns:
            Dict with safe error information for display
        """
        import traceback as tb
        
        error_hash = self.get_error_hash(exception)
        error_type = self.get_safe_exception_type(exception)
        safe_message = self.sanitize(str(exception))
        timestamp = datetime.utcnow().isoformat()
        
        # Build safe error record
        safe_record = {
            "timestamp": timestamp,
            "process": process_name,
            "error_type": error_type,
            "error_hash": error_hash,
            "message": safe_message,
            "task_id": task_id or "N/A"
        }
        
        # Sanitize context if provided
        if context:
            safe_record["context"] = {
                k: self.sanitize(str(v)) for k, v in context.items()
            }
        
        # Print safe version to notebook output
        print(f"❌ [{error_type}] {process_name} failed")
        print(f"   Error ID: {error_hash}")
        print(f"   Task ID: {task_id or 'N/A'}")
        print(f"   Message: {safe_message}")
        
        # Store full details securely if log table configured
        if self.log_table and include_traceback:
            full_traceback = tb.format_exc()
            self._store_secure_log(safe_record, full_traceback)
            print(f"   📋 Full traceback stored in: {self.log_table}")
        
        return safe_record
    
    def _store_secure_log(self, safe_record: Dict, full_traceback: str):
        """Store detailed error log in secure Delta table."""
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            
            # Create log entry with full details (stored securely, not printed)
            log_entry = {
                **safe_record,
                "full_traceback": full_traceback,
                "logged_at": datetime.utcnow().isoformat()
            }
            
            # Append to Delta table
            df = spark.createDataFrame([log_entry])
            df.write.format("delta").mode("append").saveAsTable(self.log_table)
            
        except Exception as log_error:
            # Don't fail the main process if logging fails
            print(f"   ⚠️ Could not store detailed log: {type(log_error).__name__}")
    
    def log_warning(self, process_name: str, message: str, task_id: Optional[str] = None):
        """Log a warning message safely."""
        safe_message = self.sanitize(message)
        print(f"⚠️ [{process_name}] Warning: {safe_message}")
        if task_id:
            print(f"   Task ID: {task_id}")
    
    def log_info(self, process_name: str, message: str):
        """Log an info message safely."""
        safe_message = self.sanitize(message)
        print(f"ℹ️ [{process_name}] {safe_message}")


# Convenience function for quick usage
def safe_error_message(exception: Exception, max_length: int = 200) -> str:
    """
    Quick utility to get a safe error message without full logger setup.
    
    Usage:
        except Exception as e:
            print(f"Error: {safe_error_message(e)}")
    """
    logger = SecureLogger(max_message_length=max_length)
    return f"{logger.get_safe_exception_type(exception)}: {logger.sanitize(str(exception))}"
