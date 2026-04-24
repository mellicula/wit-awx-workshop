class Budget:
    def __init__(self):
        self._limits: dict[str, float] = {}

    def set_limit(self, category: str, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Budget limit must be positive")
        self._limits[category] = amount

    def get_limit(self, category: str) -> float | None:
        return self._limits.get(category)

    def is_over_budget(self, category: str, spent: float) -> bool:
        limit = self._limits.get(category)
        if limit is None:
            return False
        # BUG: >= means "at the limit" is incorrectly counted as over budget
        return spent >= limit

    def remaining(self, category: str, spent: float) -> float | None:
        limit = self._limits.get(category)
        if limit is None:
            return None
        return round(limit - spent, 2)

    def summary(self, spent_by_category: dict[str, float]) -> dict[str, dict]:
        result = {}
        for category, limit in self._limits.items():
            spent = spent_by_category.get(category, 0.0)
            result[category] = {
                "limit": limit,
                "spent": spent,
                "remaining": round(limit - spent, 2),
                # BUG: consistent with is_over_budget bug above
                "over_budget": spent >= limit,
            }
        return result
