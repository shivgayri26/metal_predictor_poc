from datetime import datetime; import random
def scrap_metric(metal:str):
    availability=max(10,100-random.randint(0,40))
    quality=max(10,80-random.randint(0,30))
    price_impact=round((100-availability)*0.5 + (100-quality)*0.5,2)
    return {'metal':metal,'availability':availability,'quality':quality,'price_impact_index':price_impact,'checked_at':datetime.utcnow().isoformat()}
