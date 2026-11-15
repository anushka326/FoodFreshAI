# backend/app/router/auth.py
"""
FoodFresh AI - Authentication Router (Compatibility Adapter)
Re-exports the production authentication routes and current-user dependency
to ensure compatibility with both internal modules and external clients.
"""

from backend.app.deps.auth import get_current_user  # noqa: F401
from backend.app.routes.auth import router  # noqa: F401
