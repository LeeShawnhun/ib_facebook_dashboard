from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Dict
import uvicorn

# 터미널에 uvicorn main:app --reload 로 실행
app = FastAPI()

# Static files and templates setup
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Facebook credentials
ACCESS_TOKEN = 'EAAIdhh3O5lMBOyZBOfEGlIlz15VG5w8uhQaZAnTZCOki1FqnZCYtTLcvg0I80VjlQZCGZBvBDfTmOF6erPqweMRlXo0LjwoM2i52Rwz0H309uemjecjgJNaZBMRZAFP0EI5z2qPO8qnS1XqZC7ZCRm4ZBFdwDlW8VouWIFS1otjGTdpERWyFabr8lgsZBWjvpdjjckZAp'
APP_ID = '595411816343123'
APP_SECRET = '75a3b637be5da6d9b226afe1bd349e82'
AD_ACCOUNT_ID = 1596591621287444

# Initialize Facebook API
FacebookAdsApi.init(access_token=ACCESS_TOKEN, app_id=APP_ID, app_secret=APP_SECRET)

def get_ads_data() -> List[Dict]:
    """Fetch and format ads data"""
    try:
        account = AdAccount(f'act_{AD_ACCOUNT_ID}')
        ads = account.get_ads(fields=[
            'account_id', 'campaign_id', 'adset_id', 'name', 'status',
            'configured_status', 'effective_status', 'created_time',
            'updated_time', 'ad_review_feedback', 'id', 'issues_info'
        ])
        
        formatted_ads = []
        for ad in ads:
            if ad['effective_status'] == "DISAPPROVED":
                campaign_name = get_campaign_name(ad['campaign_id'])
                adset_name = get_adset_name(ad['adset_id'])
                
                formatted_ad = {
                    'account_id': ad['account_id'],
                    'campaign_id': ad['campaign_id'],
                    'campaign_name': campaign_name,
                    'adset_id': ad['adset_id'],
                    'adset_name': adset_name,
                    'ad_name': ad['name'],
                    'ad_id': ad['id'],
                    'created_time': ad['created_time'],
                    'updated_time': ad['updated_time'],
                    'status': ad['status'],
                    'configured_status': ad['configured_status'],
                    'effective_status': ad['effective_status'],
                    'rejection_reason': list(ad['ad_review_feedback']["global"].keys())[0] if "global" in ad['ad_review_feedback'] else "Unknown"
                }
                formatted_ads.append(formatted_ad)
                
        return formatted_ads
    except Exception as e:
        print(f"Error fetching ads: {str(e)}")
        return []

def get_campaign_name(campaign_id):
    try:
        campaign = Campaign(campaign_id)
        campaign_info = campaign.api_get(fields=['name'])
        return campaign_info['name']
    except Exception as e:
        print(f"Error fetching campaign name: {str(e)}")
        return None

def get_adset_name(adset_id):
    try:
        adset = AdSet(adset_id)
        adset_info = adset.api_get(fields=['name'])
        return adset_info['name']
    except Exception as e:
        print(f"Error fetching adset name: {str(e)}")
        return None

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/ads")
async def get_ads():
    ads_data = get_ads_data()
    return JSONResponse(content=ads_data)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)