import requests
from fastapi import APIRouter

router = APIRouter()


@router.get("/test-token")
def get_cj_token():
    response = requests.post(
        "https://developers.cjdropshipping.com/api2.0/v1/authentication/getAccessToken",
        json={"apiKey": "PASTE_MY_CJ_API_KEY_HERE"},
        headers={"Content-Type": "application/json"},
    )
    return response.json()
