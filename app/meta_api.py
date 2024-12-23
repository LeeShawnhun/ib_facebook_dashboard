from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from datetime import datetime
import os
from .config import AD_ACCOUNTS

class MetaAdsAPI:
    def __init__(self):
        self.api = FacebookAdsApi.init(
            access_token=os.getenv('META_ACCESS_TOKEN'),
            app_secret=os.getenv('META_APP_SECRET'),
            app_id=os.getenv('META_APP_ID')
        )

    def get_campaign_name(self, campaign_id):
        try:        
            # 캠페인 객체 생성
            campaign = Campaign(campaign_id)
            
            # fields 파라미터로 name만 지정하여 캠페인 정보 조회
            campaign_info = campaign.api_get(
                fields=['name']
            )
            
            return campaign_info['name']
        
        except Exception as e:
            print(f"Error fetching campaign name: {str(e)}")
            return None
        
    def get_adset_name(self, adset_id):
        try:
            # AdSet 객체 생성
            adset = AdSet(adset_id)
            
            # fields 파라미터로 name만 지정하여 AdSet 정보 조회
            adset_info = adset.api_get(
                fields=['name']
            )
            
            return adset_info['name']
        
        except Exception as e:
            print(f"Error fetching adset name: {str(e)}")
            return None    

    def get_rejected_ads_for_team(self, team_name: str, account_ids: list):
        rejected_ads = []
        for account_id in account_ids:
            account = AdAccount(f'act_{account_id}')
            try:
                ads = account.get_ads(
                    fields=[
                        'account_id',
                        'campaign_id',
                        'adset_id',
                        'name',
                        'effective_status',
                        'updated_time',
                        'ad_review_feedback',
                        'id'
                    ],
                    
                    params={
                        'effective_status': ['DISAPPROVED']
                    }
                )
                
                for ad in ads:
                    campaign_name = self.get_campaign_name(ad['campaign_id'])
                    adset_name = self.get_adset_name(ad['adset_id'])

                    reject_reason = "Unknown"

                    if 'ad_review_feedback' in ad:
                        feedback = ad['ad_review_feedback'].get('global', {})
                        if feedback:
                            reject_reason = list(feedback.keys())[0] if feedback else "Unknown"

                    rejected_ads.append({
                        'campaign': campaign_name,
                        'adgroup': adset_name,
                        'ad': ad['name'],
                        'rejectReasaon': reject_reason,
                        'lastModified': datetime.strptime(ad['updated_time'], '%Y-%m-%dT%H:%M:%S%z'),
                        'team': team_name
                    })

            except Exception as e:
                print(f"Error fetching ads for account {account_id}: {str(e)}")
                
        return rejected_ads

    def get_all_rejected_ads(self):
        all_rejected_ads = []
        for team_name, account_ids in AD_ACCOUNTS.items():
            team_ads = self.get_rejected_ads_for_team(team_name, account_ids)
            all_rejected_ads.extend(team_ads)
        return all_rejected_ads