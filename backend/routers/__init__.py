"""Route definitions: one module per route path.

`ALL_ROUTERS` is the single registry the gateway (main.py) mounts.
Adding a new route = add a module here and append its router.
"""

from routers import chat, claims, health, outlets, search, stories, story

ALL_ROUTERS = [
    health.router,
    story.router,
    claims.router,
    stories.router,
    chat.router,
    search.router,
    outlets.router,
]
