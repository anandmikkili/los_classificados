"""Import all callback modules so their @app.callback decorators are registered."""
from . import routing          # noqa: F401
from . import home_callbacks   # noqa: F401
from . import browse_callbacks # noqa: F401
from . import post_ad_callbacks# noqa: F401
from . import leads_callbacks  # noqa: F401
from . import prime_callbacks         # noqa: F401
from . import my_listings_callbacks   # noqa: F401
from . import providers_callbacks     # noqa: F401
from . import dashboard_callbacks     # noqa: F401
