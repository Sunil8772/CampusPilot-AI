def format_availability_result(result, resource_type):
    if not result or not result.get("success"):
        return result.get("message", "Availability check failed.") if result else "No result returned."
    resources = result.get("available_resources", [])
    if not resources:
        return f"No {resource_type.replace('_', ' ')} resources were found for that time. No booking was made."
    names = [f"{r.get('name')} (capacity {r.get('capacity')})" for r in resources]
    return "Available options (not booked): " + "; ".join(names)
