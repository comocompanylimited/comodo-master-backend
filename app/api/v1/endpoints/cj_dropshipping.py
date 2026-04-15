import requests
from fastapi import APIRouter

router = APIRouter()


@router.get("/test-token")
def get_cj_token():
    response = requests.post(
        "https://developers.cjdropshipping.com/api2.0/v1/authentication/getAccessToken",
        json={"apiKey": "CJ5330994@api@87b2693dfc4d423aa432c499eab5aaa3"},
        headers={"Content-Type": "application/json"},
    )
    return response.json()
