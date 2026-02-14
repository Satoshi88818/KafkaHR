"""JSON logging formatter for structured logging."""

import json
import time
from logging import Formatter


class JsonFormatter(Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        """
        Format log record as JSON.
        
        Args:
            record: LogRecord instance
        
        Returns:
            JSON formatted log string
        """
        data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created)),
            'level': record.levelname,
            'message': record.msg,
            'module': record.module,
            'funcName': record.funcName,
            'lineno': record.lineno,
        }
        if record.exc_info:
            data['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(data)
