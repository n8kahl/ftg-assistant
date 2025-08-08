from services.schema import FixResponse
from services.strategies import generate_plan

async def propose_fix(ctx: dict) -> FixResponse:
    symbol = ctx.get("symbol","SPY")
    side = ctx.get("side","calls")
    plan = await generate_plan(symbol)
    action = "review_and_flatten"
    if side == "shares":
        action = "add_protective_put"; plan.reasons.append("Protective put to cap downside")
        plan.options_overlay.type = "puts"; plan.options_overlay.dte = 3; plan.options_overlay.delta_target = 0.40
    elif side == "calls":
        action = "convert_to_debit_vertical"; plan.reasons.append("Convert to vertical to reduce theta")
    elif side == "puts":
        action = "roll_out_or_convert_to_spread"; plan.reasons.append("Roll for credit or convert to spread")
    from services.schema import FixResponse as FR
    return FR(action=action, plan=plan)
