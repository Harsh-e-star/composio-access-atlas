"""Dataset module importing all 10 categories (100 apps)."""
from .crm_sales import CRM_SALES
from .support_helpdesk import SUPPORT_HELPDESK
from .communications import COMMUNICATIONS
from .marketing_social import MARKETING_SOCIAL
from .ecommerce import ECOMMERCE
from .data_seo_scraping import DATA_SEO_SCRAPING
from .developer_infra import DEVELOPER_INFRA
from .productivity_projects import PRODUCTIVITY_PROJECTS
from .finance_fintech import FINANCE_FINTECH
from .ai_research_media import AI_RESEARCH_MEDIA

ALL_APPS = (
    CRM_SALES
    + SUPPORT_HELPDESK
    + COMMUNICATIONS
    + MARKETING_SOCIAL
    + ECOMMERCE
    + DATA_SEO_SCRAPING
    + DEVELOPER_INFRA
    + PRODUCTIVITY_PROJECTS
    + FINANCE_FINTECH
    + AI_RESEARCH_MEDIA
)

__all__ = [
    "ALL_APPS",
    "CRM_SALES",
    "SUPPORT_HELPDESK",
    "COMMUNICATIONS",
    "MARKETING_SOCIAL",
    "ECOMMERCE",
    "DATA_SEO_SCRAPING",
    "DEVELOPER_INFRA",
    "PRODUCTIVITY_PROJECTS",
    "FINANCE_FINTECH",
    "AI_RESEARCH_MEDIA",
]
