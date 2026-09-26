def compare_models(statistical:dict,ml:dict)->dict:
    candidates=[statistical,ml]
    candidates=[x for x in candidates if x.get("mae") is not None]
    if not candidates:return {"models":[],"selected":None}
    ranked=sorted(candidates,key=lambda x:(x.get("mae",float("inf")),-x.get("direction_accuracy",0)))
    return {"models":ranked,"selected":ranked[0].get("model")}
