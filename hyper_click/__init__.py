def get_enabled_scopes(settings):
    return {
        selector: rule
        for selector, rule in settings.get("scopes", {}).items()
        if (rule or {}).get("enabled", True)
    }
