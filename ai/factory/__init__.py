"""
Bot Factory

Auto-discovers bots from the bots/ folder and exposes a single
FastAPI router containing all enabled bots.

Embedded in another project:
    from ai.factory import factory_router
    app.include_router(factory_router, prefix=prefix)

Standalone:
    uvicorn factory.main:app --reload --port 8080
"""
import yaml
from pathlib import Path
from fastapi import APIRouter
from .core.router import create_bot_router


def _discover_and_build_router() -> APIRouter:
    """
    Scan bots/ folder, find enabled bots, and combine
    their routers into one parent router.
    """
    router = APIRouter()
    bots_path = Path(__file__).parent / 'bots'

    if not bots_path.exists():
        return router

    for bot_dir in sorted(bots_path.iterdir()):
        if not bot_dir.is_dir():
            continue

        config_path = bot_dir / 'config.yml'
        if not config_path.exists():
            continue

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            bot_config = config.get('bot', {})
            bot_id = bot_config.get('id', bot_dir.name)

            if bot_config.get('enabled', False):
                bot_router = create_bot_router(bot_id)
                router.include_router(bot_router)
                print(f"  Bot Factory: {bot_id} (enabled)")
            else:
                print(f"  Bot Factory: {bot_id} (disabled, skipping)")

        except Exception as e:
            print(f"  Bot Factory: warning — could not read {config_path}: {e}")

    return router


# Build the router at import time — same pattern as ai/router.py
factory_router = _discover_and_build_router()