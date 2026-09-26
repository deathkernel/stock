def fuse_research_signals(market:dict,fundamentals:dict|None=None,news:dict|None=None)->dict:
    parts=[];weights=[]
    agreement=float(market.get("agreement",0.5))
    parts.append(agreement);weights.append(.50)
    if fundamentals:
        coverage=float(fundamentals.get("coverage",0))
        if coverage:
            signal=(fundamentals.get("positive_count",0)-fundamentals.get("negative_count",0))/max(coverage,1)
            parts.append(.5+.5*max(-1,min(1,signal)));weights.append(.25)
    if news:
        articles=int(news.get("articles",0))
        if articles:
            sentiment=float(news.get("mean_sentiment",0))
            parts.append(.5+.5*max(-1,min(1,sentiment)));weights.append(.25)
    total=sum(weights)
    score=sum(v*w for v,w in zip(parts,weights))/max(total,1e-9)
    return {"score":float(score),"components":len(parts),"weights_used":weights}
