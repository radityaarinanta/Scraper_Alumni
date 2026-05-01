import time
from apify_client import ApifyClient

class ScraperEngine:
    def __init__(self, token):
        self.client = ApifyClient(token)

    def search_by_name(self, first, last):
        payload = {
            "firstName": first,
            "lastName": last,
            "profileScraperMode": "Full + email search",
            "strictSearch": False,
            "maxPages": 1
        }
        
        try:
            run = self.client.actor("harvestapi/linkedin-profile-search-by-name").call(run_input=payload)
            return self.client.dataset(run["defaultDatasetId"]).list_items().items
        except Exception as e:
            return str(e)

    def refresh_client(self, new_token):
        self.client = ApifyClient(new_token)
