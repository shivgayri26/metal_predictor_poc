import asyncio, random
from datetime import datetime
class PriceFetcher:
    def __init__(self): self.cache = {}
    async def fetch_from_remote(self, metal: str) -> dict:
        await asyncio.sleep(0.05)
        base = {'gold':1967.5,'silver':22.48,'copper':4.15,'aluminium':0.95,'nickel':22.3}
        price = base.get(metal.lower(),1.0)*(1+random.uniform(-0.01,0.01))
        return {'price': round(price,4), 'ts': datetime.utcnow().isoformat()}
    async def get_price(self, metal: str) -> dict:
        if metal in self.cache: return self.cache[metal]
        data = await self.fetch_from_remote(metal); self.cache[metal]=data; return data
