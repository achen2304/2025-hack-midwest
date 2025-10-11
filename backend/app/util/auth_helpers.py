"""
Helper utilities for authentication
"""
from starlette.requests import Request


def get_user_id(request: Request) -> str:
    """Helper to extract user_id from request state"""
    return request.state.user["user_id"]


def get_user_email(request: Request) -> str:
    """Helper to extract user email from request state"""
    return request.state.user.get("email", "")


def get_user_name(request: Request) -> str:
    """Helper to extract user name from request state"""
    return request.state.user.get("name", "")
