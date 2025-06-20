from fastapi import APIRouter, Request, Response
import httpx

router = APIRouter()


async def proxy_request(request: Request, upstream_url: str):
    try:
        async with httpx.AsyncClient() as client:
            body = await request.body()
            proxy_response = await client.request(
                method=request.method,
                url=upstream_url,
                headers={
                    key: value for key, value in request.headers.items()
                    if key.lower() not in ["host", "content-length", "transfer-encoding", "connection"]
                },
                content=body
            )
            return Response(
                content=proxy_response.content,
                status_code=proxy_response.status_code,
                headers={
                    key: value for key, value in proxy_response.headers.items()
                    if key.lower() not in ["content-encoding", "transfer-encoding", "connection"]
                },
            )
    except Exception as e:
        return Response(content=f"Erro ao redirecionar requisição: {str(e)}", status_code=500)


@router.api_route("/payments/{path:path}", methods=["GET"])
async def list_payments_proxy(path: str, request: Request):
    upstream_url = f"http://payment-service:5002/api/v1/payments/{path}"
    return await proxy_request(request, upstream_url)


@router.api_route("/payments-confirm/{path:path}", methods=["POST"])
async def confirm_payment_proxy(path: str, request: Request):
    upstream_url = f"http://payment-service:5002/api/v1/confirm/{path}"
    return await proxy_request(request, upstream_url)

