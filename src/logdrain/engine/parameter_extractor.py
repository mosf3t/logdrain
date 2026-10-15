import re
from typing import List, Any
from logdrain.models import ParameterDetail

class ParameterExtractor:
    """Classifies and validates parameters extracted from Drain3 log templates."""

    FILE_PATH_REGEX = re.compile(r'^/[\w\-\./]+(?:\.zip|\.installation|\.variables|\.urp)?$')
    PROGRAM_NAME_REGEX = re.compile(r'^["\']?[A-Za-z0-9_\-\s]+["\']?$')
    STATE_REGEX = re.compile(r'^(PLAYING|PAUSED|STOPPED|NORMAL|PROTECTIVE_STOP|SAFEGUARD_STOP|RUNNING|POSITION|SUCCESS)$', re.IGNORECASE)

    def classify_parameter(self, param_value: Any) -> ParameterDetail:
        # Drain3 returns ExtractedParameter objects with a .value attribute
        val_str = param_value.value if hasattr(param_value, 'value') else str(param_value)
        cleaned = val_str.strip()
        
        # Check if it's a file path
        if self.FILE_PATH_REGEX.search(cleaned):
            return ParameterDetail(value=cleaned, category="FILE_PATH", normalized_name="file_path")
        
        # Check if it's a known state or mode keyword
        if self.STATE_REGEX.match(cleaned.strip('"\'')):
            return ParameterDetail(value=cleaned, category="STATE_OR_MODE", normalized_name="state")
            
        # Check if it's numeric
        if re.match(r'^-?\d+(?:\.\d+)?$', cleaned):
            return ParameterDetail(value=cleaned, category="NUMERIC", normalized_name="numeric_val")
            
        # Default category
        return ParameterDetail(value=cleaned, category="PROGRAM_OR_TEXT", normalized_name="text_param")

    def process_parameters(self, raw_parameters: List[Any]) -> List[ParameterDetail]:
        return [self.classify_parameter(p) for p in raw_parameters]
