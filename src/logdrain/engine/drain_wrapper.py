from typing import Dict, Any, List
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from drain3.masking import MaskingInstruction
from logdrain.engine.parameter_extractor import ParameterExtractor
from logdrain.models import ParameterDetail

class DrainEngine:
    def __init__(self, use_persistence: bool = False):
        self.config = TemplateMinerConfig()
        
        self.config.masking_instructions = [
            MaskingInstruction(
                r'/[\w\-\./]+(?:recording[\d_]+\.zip|\.installation|\.variables)', 
                'FILE_PATH'
            )
        ]
        
        self.config.profiling_enabled = False
        self.template_miner = TemplateMiner(persistence_handler=None, config=self.config)
        self.extractor = ParameterExtractor()

    def process_message(self, message: str) -> Dict[str, Any]:
        result = self.template_miner.add_log_message(message)
        cluster_id = result.get("cluster_id")
        template_mined = result.get("template_mined")
        raw_parameters = self.template_miner.extract_parameters(template_mined, message) or []
        
        # Process and categorize parameters
        structured_params = self.extractor.process_parameters(raw_parameters)
        
        return {
            "cluster_id": cluster_id,
            "template_text": template_mined,
            "change_type": result.get("change_type"),
            "parameters": structured_params,
        }

    def get_cluster_stats(self) -> List[Dict[str, Any]]:
        clusters = []
        for cluster in self.template_miner.drain.clusters:
            clusters.append({
                "cluster_id": cluster.cluster_id,
                "template": cluster.get_template(),
                "size": cluster.size,
            })
        return clusters
