# Backward compatibility wrapper for collector.py
# New collectors should be imported from the 'collectors' package.
from collectors.coupang import CoupangPartnersClient

__all__ = ["CoupangPartnersClient"]
