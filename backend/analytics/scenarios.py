def scenarios(last_price:float,forecast_price:float,volatility:float)->list[dict]:
    move=forecast_price/last_price-1 if last_price else 0
    shock=max(volatility,.05)
    return [{"name":"base","expected_move":move,"price":forecast_price},
            {"name":"upside","expected_move":move+shock,"price":last_price*(1+move+shock)},
            {"name":"downside","expected_move":move-shock,"price":max(0,last_price*(1+move-shock))}]
