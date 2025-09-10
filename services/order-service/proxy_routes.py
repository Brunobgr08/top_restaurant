# import os
# import httpx
# from fastapi import APIRouter, Request, Response
# from dotenv import load_dotenv

# load_dotenv()

# router = APIRouter()

# PAYMENT_HOST = os.getenv("PAYMENT_HOST", "payment-service:5002")

# async def proxy_request(request: Request, upstream_url: str):
#     try:
#         async with httpx.AsyncClient() as client:
#             body = await request.body()
#             proxy_response = await client.request(
#                 method=request.method,
#                 url=upstream_url,
#                 headers={
#                     key: value for key, value in request.headers.items()
#                     if key.lower() not in ["host", "content-length", "transfer-encoding", "connection"]
#                 },
#                 content=body
#             )
#             return Response(
#                 content=proxy_response.content,
#                 status_code=proxy_response.status_code,
#                 headers={
#                     key: value for key, value in proxy_response.headers.items()
#                     if key.lower() not in ["content-encoding", "transfer-encoding", "connection"]
#                 },
#             )
#     except Exception as e:
#         return Response(content=f"Erro ao redirecionar requisição: {str(e)}", status_code=500)


# @router.api_route("/payments", methods=["GET"])
# async def list_payments_proxy(request: Request):
#     upstream_url = f"https://{PAYMENT_HOST}/api/v1/payments"
#     return await proxy_request(request, upstream_url)


# @router.api_route("/payments/confirm/{order_id}", methods=["PUT"])
# async def confirm_payment_proxy(order_id: str, request: Request):
#     upstream_url = f"https://{PAYMENT_HOST}/api/v1/payments/confirm/{order_id}"
#     return await proxy_request(request, upstream_url)

import logging

import os
import httpx
from fastapi import APIRouter, Request, Response
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(handler)

router = APIRouter()

PAYMENT_SERVICE_URL = os.getenv(
    "PAYMENT_SERVICE_URL",
    "payment-service:5002"
)

async def proxy_request(request: Request, upstream_url: str):
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"------>>> Upstream_url: {upstream_url}")
            headers = {
                key: value for key, value in request.headers.items()
                if key.lower() not in ["host", "content-length"]
            }
            logger.info(f"------>>> Headers: {headers}")
            url_with_params = str(request.url).replace(str(request.base_url), upstream_url)
            logger.info(f"------>>> Url_with_params: {url_with_params}")
            proxy_response = await client.request(
                method=request.method,
                url=url_with_params,
                headers=headers,
                content=await request.body(),
                timeout=30.0
            )
            logger.info(f"------>>> Proxy_response: {proxy_response}")
            return Response(
                content=proxy_response.content,
                status_code=proxy_response.status_code,
                headers=dict(proxy_response.headers),
            )
    except httpx.ConnectError:
        return Response(content="Payment service indisponível", status_code=503)
    except Exception as e:
        return Response(content=f"Erro ao redirecionar requisição: {str(e)}", status_code=500)

@router.api_route("/payments", methods=["GET"])
async def list_payments_proxy(request: Request):
    upstream_url = f"{PAYMENT_SERVICE_URL}/api/v1/payments"
    return await proxy_request(request, upstream_url)

@router.api_route("/payments/confirm/{order_id}", methods=["PUT"])
async def confirm_payment_proxy(order_id: str, request: Request):
    upstream_url = f"{PAYMENT_SERVICE_URL}/api/v1/payments/confirm/{order_id}"
    return await proxy_request(request, upstream_url)
