from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse



class AuthMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, exclude_from_auth):
        super().__init__(app)
        self.excluded_path = exclude_from_auth

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.excluded_path:
            return await call_next(request)

        userid = request.session.get('userid')

        if not userid:
            return JSONResponse(
                status_code=401,
                content={'detail': 'Not authenticated'},
            )

        request.state.userid = userid

        return await call_next(request)
