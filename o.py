from services.storage_service import StorageService

StorageService.upload_cycle_file(
    "uploads/test.txt",
    "debug/test.txt"
)

print("UPLOAD OK")
