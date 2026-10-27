from data import BUSINESSES


def validate(budget, hours):
    """입력값 검증. 문제가 있으면 메시지, 없으면 None"""
    if budget < 0:
        return "예산은 0원 이상이어야 해요."
    if hours <= 0:
        return "주당 투자 가능 시간은 0보다 커야 해요."
    if hours > 168:
        return "주당 시간은 168시간을 넘을 수 없어요."
    return None


def score_business(b, budget, hours, level, skills):
    """사업 하나의 추천 점수(0~100)와 이유 목록을 계산"""
    reasons = []

    # 1) 시간 점수: 필요 시간 대비 내 시간 (최대 1)
    time_score = min(hours / b["hours"], 1)
    if time_score >= 1:
        reasons.append(f"주 {b['hours']}시간 필요, 내 시간으로 충분해요")
    else:
        reasons.append(f"주 {b['hours']}시간이 필요해서 시간이 다소 부족해요")

    # 2) 난이도 점수: 내 경험 수준보다 어려울수록 감점
    gap = max(b["difficulty"] - level, 0)
    level_score = max(1 - gap * 0.3, 0)
    if gap == 0:
        reasons.append("내 경험 수준에 맞는 난이도예요")
    else:
        reasons.append(f"내 수준보다 난이도가 {gap}단계 높아요")

    # 3) 기술 점수: 내가 가진 기술과 겹치는 비율
    if skills:
        matched = set(skills) & set(b["skills"])
        skill_score = len(matched) / len(skills)
        if matched:
            reasons.append("내 강점과 맞는 기술: " + ", ".join(sorted(matched)))
    else:
        skill_score = 0.5

    # 4) 예산 점수: 예산이 남을수록 높음 (비용 0원이면 만점)
    if b["cost"] == 0:
        budget_score = 1.0
    else:
        budget_score = 1 - b["cost"] / budget
    reasons.append(f"초기비용 약 {b['cost']}만원")

    total = 0.3 * time_score + 0.3 * level_score + 0.25 * skill_score + 0.15 * budget_score
    return round(total * 100), reasons


def recommend(field, budget, hours, level, skills, top_n=3):
    """조건에 맞는 사업을 점수순으로 추천. (결과 목록, 안내 메시지) 반환"""
    candidates = [
        b for b in BUSINESSES
        if (field == "전체" or b["field"] == field) and b["cost"] <= budget
    ]
    notice = None

    # 예산이 부족해서 후보가 없는 경우: 가장 저렴한 사업 안내
    if not candidates:
        pool = [b for b in BUSINESSES if field == "전체" or b["field"] == field]
        if not pool:
            return [], "해당 분야의 사업 데이터가 없어요."
        cheapest = min(b["cost"] for b in pool)
        return [], f"예산이 부족해요. 이 분야에서 가장 저렴한 사업은 약 {cheapest}만원이 필요해요."

    results = []
    for b in candidates:
        score, reasons = score_business(b, budget, hours, level, skills)
        results.append({"biz": b, "score": score, "reasons": reasons})

    results.sort(key=lambda r: r["score"], reverse=True)
    return results, notice
