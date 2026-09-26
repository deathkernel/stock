import re
import numpy as np

EVENT_TERMS={
    "earnings":["earnings","eps","revenue","guidance","quarter"],
    "corporate_action":["acquisition","merger","buyback","dividend","split"],
    "legal":["lawsuit","investigation","regulator","fine","settlement"],
    "management":["ceo","cfo","resigns","appointed","management"],
    "product":["launch","approval","product","contract","order"],
}

def classify_event(text:str)->str:
    t=text.lower()
    for event,terms in EVENT_TERMS.items():
        if any(re.search(r"\b"+re.escape(term)+r"\b",t) for term in terms):
            return event
    return "general"

def aggregate_news(items:list[dict])->dict:
    scores=[];events={}
    for item in items:
        score=item.get("sentiment_score")
        if score is None:
            score=0.0
        try: score=float(score)
        except (TypeError,ValueError): score=0.0
        text=f"{item.get('headline','')} {item.get('summary','')}"
        event=classify_event(text)
        scores.append(score);events[event]=events.get(event,0)+1
    return {"articles":len(items),"mean_sentiment":float(np.mean(scores)) if scores else 0.0,
            "positive_articles":sum(x>0.15 for x in scores),"negative_articles":sum(x<-0.15 for x in scores),
            "event_counts":events}
