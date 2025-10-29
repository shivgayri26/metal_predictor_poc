from datetime import datetime
def geopolitics_signal(region:str):
    score=50.0
    events=[{'date':datetime.utcnow().isoformat(),'title':f'Mocked event in {region}','impact':'moderate'}]
    return {'region':region,'risk_score':score,'events':events}
