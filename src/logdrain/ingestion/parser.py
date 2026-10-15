import re
from datetime import datetime
from typing import List, Optional
from logdrain.models import LogRecord

# Matches standard Polyscope lines starting directly with a timestamp (supporting malformed like '026-') and severity
START_REGEX = re.compile(
    r'(?:^|\n)([0-9\?\-]{3,5}[\-\s]?[0-9\?\-]{2}[\-\s]?[0-9\?\-]{2}\s+[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3})\s+([A-Z_TRACE]+)\b'
)

META_REGEX = re.compile(
    r'\{\s*thread:\s*(.*?),\s*loggerClass:\s*(.*?)\}\s*$',
    re.DOTALL
)

class PolyscopeLogParser:
    def parse_file(self, file_path: str) -> List[LogRecord]:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return self.parse_string(content)

    def parse_string(self, log_content: str) -> List[LogRecord]:
        matches = list(START_REGEX.finditer(log_content))
        if not matches:
            if not log_content.strip():
                return []
            # If no standard timestamps are found, return empty or handle gracefully
            return []

        records: List[LogRecord] = []
        for i, match in enumerate(matches):
            start_idx = match.start()
            if match.group(0).startswith('\n'):
                start_idx += 1  # Adjust past newline separator

            # Bounded strictly by the next timestamp match
            end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(log_content)
            raw_text = log_content[start_idx:end_idx].strip()
            
            ts_str = match.group(1)
            severity = match.group(2)
            source_line = log_content.count('\n', 0, start_idx) + 1

            record = self._build_record(i + 1, raw_text, ts_str, severity, source_line)
            records.append(record)

        return records

    def _build_record(self, record_id: int, raw_text: str, ts_str: str, severity: str, source_line: int) -> LogRecord:
        thread = "UNKNOWN"
        logger_class = "UNKNOWN"
        body_part = raw_text

        # Extract trailing metadata and strip accidental surrounding quotes
        meta_match = META_REGEX.search(raw_text)
        if meta_match:
            thread = re.sub(r'\s+', ' ', meta_match.group(1)).strip().strip('"\'')
            logger_class = re.sub(r'\s+', ' ', meta_match.group(2)).strip().strip('"\'')
            body_part = raw_text[:meta_match.start()].strip()

        # Strip leading header prefix (timestamp + severity)
        header_prefix_pattern = r'^[0-9\?\-]{3,5}[\-\s]?[0-9\?\-]{2}[\-\s]?[0-9\?\-]{2}\s+[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}\s+[A-Z_TRACE]+\s+'
        message_body = re.sub(header_prefix_pattern, '', body_part, count=1, flags=re.DOTALL).strip()

        # Clean and prevent leading dashes and raw indentation whitespace from the message body
        message_body = re.sub(r'^-\s*', '', message_body).strip()

        # Parse timestamp safely and correct malformed years (e.g., '026-' -> '2026-')
        parsed_dt = None
        is_malformed = False
        try:
            cleaned_ts = ts_str.replace('?', '0')
            cleaned_ts = re.sub(r'^(\d{3})-', r'2\1-', cleaned_ts)
            if cleaned_ts.startswith('0'):
                cleaned_ts = '2' + cleaned_ts[1:]
            parsed_dt = datetime.strptime(cleaned_ts, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            is_malformed = True

        return LogRecord(
            record_id=record_id,
            raw_text=raw_text,
            timestamp=parsed_dt,
            severity=severity,
            message_body=message_body,
            thread=thread,
            logger_class=logger_class,
            source_line=source_line,
            is_malformed=is_malformed
        )
