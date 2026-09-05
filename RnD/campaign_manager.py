import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class CampaignStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class CampaignManager:
    """
    Manager for Research Campaigns.
    Handles lifecycle, configuration, and reporting of R&D campaigns.
    """
    
    def __init__(self, db_connector):
        self.db_connector = db_connector
        self.active_campaigns = {}

    def create_campaign(
        self, 
        name: str, 
        assets: List[str], 
        directions: List[str], 
        timeframes: List[str],
        tools: List[str],
        start_date: str,
        end_date: str,
        validation_method: str = "WALK_FORWARD"
    ) -> str:
        campaign_id = f"RND-CAM-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        
        config = {
            "campaign_id": campaign_id,
            "name": name,
            "assets": assets,
            "directions": directions,
            "timeframes": timeframes,
            "tools": tools,
            "start_date": start_date,
            "end_date": end_date,
            "validation_method": validation_method,
            "created_at": datetime.now().isoformat(),
            "status": CampaignStatus.PENDING.value
        }
        
        # Save to DB
        self.db_connector.save_campaign(config)
        self.active_campaigns[campaign_id] = config
        
        return campaign_id

    def start_campaign(self, campaign_id: str):
        if campaign_id not in self.active_campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")
            
        self.active_campaigns[campaign_id]['status'] = CampaignStatus.RUNNING.value
        self.db_connector.update_campaign_status(campaign_id, CampaignStatus.RUNNING.value)

    def complete_campaign(self, campaign_id: str):
        if campaign_id not in self.active_campaigns:
            return
            
        self.active_campaigns[campaign_id]['status'] = CampaignStatus.COMPLETED.value
        self.db_connector.update_campaign_status(campaign_id, CampaignStatus.COMPLETED.value)

    def fail_campaign(self, campaign_id: str, reason: str):
        if campaign_id not in self.active_campaigns:
            return
            
        self.active_campaigns[campaign_id]['status'] = CampaignStatus.FAILED.value
        self.db_connector.update_campaign_status(campaign_id, CampaignStatus.FAILED.value, reason=reason)

    def get_campaign_status(self, campaign_id: str) -> Optional[Dict]:
        return self.active_campaigns.get(campaign_id)