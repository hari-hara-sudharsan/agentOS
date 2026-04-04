try:
    from backend.integrations import integration_service
    print("Compilation Success: integration_service is valid.")
except Exception as e:
    print(f"Compilation Failure: {e}")
    import traceback
    traceback.print_exc()
