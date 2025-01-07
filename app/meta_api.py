from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from datetime import datetime
import os
from .config import AD_ACCOUNTS

# meta_api.py 수정
class MetaAdsAPI:
    def __init__(self):
        self.api = FacebookAdsApi.init(
            access_token=os.getenv('META_ACCESS_TOKEN'),
            app_secret=os.getenv('META_APP_SECRET'),
            app_id=os.getenv('META_APP_ID')
        )

    def get_account_name(self, account_id: str) -> tuple[str, str]:
        for team, accounts in AD_ACCOUNTS.items():
            for account_name, acc_id in accounts.items():
                if acc_id == account_id:
                    return team, account_name
        return "unknown", "unknown"
    
    def get_campaign_name(self, campaign_id):
        try:        
            campaign = Campaign(campaign_id)

            campaign_info = campaign.api_get(
                fields=['name']
            )

            return campaign_info['name']

        except Exception as e:
            print(f"Error fetching campaign name: {str(e)}")
            return None

    def get_adset_name(self, adset_id):
        try:
            adset = AdSet(adset_id)

            adset_info = adset.api_get(
                fields=['name']
            )

            return adset_info['name']

        except Exception as e:
            print(f"Error fetching adset name: {str(e)}")
            return None

    def get_rejected_ads_for_team(self, team_name: str, accounts: dict):
        rejected_ads = []
        for account_name, account_id in accounts.items():
            account = AdAccount(f'act_{account_id}')
            try:
                ads = account.get_ads(
                    fields=[
                        'id',
                        'name',
                        'campaign_id',
                        'adset_id',
                        'effective_status',
                        'updated_time',
                        'ad_review_feedback'
                    ],
                    params={'effective_status': ['DISAPPROVED']}
                )
                
                for ad in ads:
                    campaign_name = self.get_campaign_name(ad['campaign_id'])
                    adset_name = self.get_adset_name(ad['adset_id'])

                    reject_reason = "Unknown"
                    if 'ad_review_feedback' in ad:
                        feedback = ad['ad_review_feedback'].get('global', {})
                        if feedback:
                            reject_reason = list(feedback.keys())[0]

                    rejected_ads.append({
                        'team': team_name,
                        'campaign': campaign_name,
                        'adgroup': adset_name,
                        'ad_id': ad['id'],
                        'ad_name': ad['name'],
                        'account_name': account_name,
                        'reject_reason': reject_reason,
                        'last_modified': datetime.strptime(
                            ad['updated_time'], 
                            '%Y-%m-%dT%H:%M:%S%z'
                        ),
                        'is_active': True
                    })

            except Exception as e:
                print(f"Error fetching ads for account {account_id}: {str(e)}")
                
        return rejected_ads

    def get_all_rejected_ads(self):
        all_rejected_ads = []
        for team_name, accounts in AD_ACCOUNTS.items():
            team_ads = self.get_rejected_ads_for_team(team_name, accounts)
            all_rejected_ads.extend(team_ads)
        return all_rejected_ads