from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Mock the files list API
        page.route("**/api/files/list*", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='''{
                "files": [
                    {
                        "id": "123",
                        "filename": "test_data.csv",
                        "uploaded_at": "2023-10-27T10:00:00",
                        "status": "completed",
                        "file_size_mb": 1.5,
                        "total_rows": 100,
                        "imported_rows": 100,
                        "failed_rows": 0,
                        "progress": 100,
                        "period": "Oct 2023",
                        "storage_path": "/tmp/test.csv",
                        "import_source": "csv_upload",
                        "import_type": "sales"
                    }
                ]
            }'''
        ))

        # Navigate to files page
        page.goto("http://localhost:3000/files")

        # Wait for table to load
        expect(page.get_by_text("test_data.csv")).to_be_visible(timeout=10000)

        # Find delete button. The aria-label is "Удалить test_data.csv"
        delete_btn = page.get_by_label("Удалить test_data.csv")
        delete_btn.click()

        # Check for modal
        expect(page.get_by_text("Удаление файла")).to_be_visible()

        # Take screenshot
        page.screenshot(path="verification/verification.png")

        browser.close()

if __name__ == "__main__":
    run()
