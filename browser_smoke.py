"""Browser smoke tests using synthetic responses; never creates real customers or deals."""
from playwright.sync_api import sync_playwright, expect
from datetime import datetime, timedelta, timezone

def main():
    now=datetime.now(timezone.utc)
    offer=dict(id="test-only",title="Browser test chair",retailer_name="Test retailer",url="https://example.com/chair",price=99.95,category="retail",published=True,verified_at=now.isoformat(),expires_at=(now+timedelta(days=1)).isoformat())
    expired=dict(offer,id="expired",title="Expired test item",expires_at=(now-timedelta(days=1)).isoformat())
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page(viewport={"width":390,"height":844})
        errors=[]
        page.on("pageerror",lambda error: errors.append(str(error)))
        page.route("**/rest/v1/public_deals?*",lambda route:route.fulfill(json=[offer,expired],headers={"access-control-allow-origin":"*"}))
        page.goto("http://127.0.0.1:8765/index.html")
        expect(page.locator("#publicGrid")).to_contain_text("Browser test chair")
        expect(page.locator("#publicGrid")).not_to_contain_text("Expired test item")
        expect(page.locator("#showExamples")).not_to_be_checked()
        page.locator("#publicQuery").fill("missing item")
        expect(page.locator("#publicStatus")).to_contain_text("No matching")
        page.locator("#publicQuery").clear()
        page.locator("#publicCategory").select_option("vehicle")
        expect(page.locator("#publicGrid article")).to_have_count(0)
        page.locator("#publicCategory").select_option("all")
        expect(page.locator("#publicGrid article")).to_have_count(1)
        page.locator('[data-feature="car"]').click()
        expect(page.locator("#carPanel")).to_be_visible()
        expect(page.locator("#publicQuery")).to_be_visible()
        page.locator('[data-feature="flip"]').click()
        expect(page.locator("#productCalc")).to_be_visible()
        page.locator("#buy").fill("100")
        page.locator("#sell").fill("150")
        page.locator("#fee").fill("10")
        page.locator("#cost").fill("5")
        expect(page.locator("#result")).to_contain_text("30")
        page.goto("http://127.0.0.1:8765/account.html")
        expect(page.locator("#auth")).to_be_visible()
        expect(page.locator("#private")).to_be_hidden()
        expect(page.locator("#adminPanel")).to_be_hidden()
        expect(page.locator("#resetPanel")).to_be_hidden()
        requests=[]
        def auth_mock(route):
            request=route.request
            headers={"access-control-allow-origin":"*","access-control-allow-methods":"GET,POST,PUT,OPTIONS","access-control-allow-headers":"apikey,authorization,content-type"}
            if request.method=="OPTIONS":
                route.fulfill(status=204,headers=headers)
                return
            requests.append((request.method,request.url,request.post_data_json if request.post_data else None))
            route.fulfill(status=200,json={},headers=headers)
        page.route("**/auth/v1/**",auth_mock)
        page.locator("summary").filter(has_text="Forgot your password?").click()
        page.locator("#recover input").fill("test@example.invalid")
        page.locator("#recover button").click()
        expect(page.locator("#status")).to_contain_text("password reset link")
        assert any(method=="POST" and "/recover?" in url for method,url,_ in requests)
        page.goto("about:blank")
        page.goto("http://127.0.0.1:8765/account.html#access_token=synthetic-test-token&type=recovery")
        expect(page.locator("#resetPanel")).to_be_visible()
        expect(page.locator("#private")).to_be_hidden()
        assert "access_token" not in page.url
        page.locator("#resetPassword [name=password]").fill("Test-password-123")
        page.locator("#resetPassword [name=confirm]").fill("Mismatch-password-123")
        page.locator("#resetPassword button[type=submit], #resetPassword button:not([type])").first.click()
        expect(page.locator("#status")).to_contain_text("Passwords do not match")
        assert not any(method=="PUT" for method,_,_ in requests)
        page.locator("#resetPassword [name=confirm]").fill("Test-password-123")
        page.locator("#resetPassword button[type=submit], #resetPassword button:not([type])").first.click()
        expect(page.locator("#status")).to_contain_text("Password updated")
        expect(page.locator("#auth")).to_be_visible()
        expect(page.locator("#resetPanel")).to_be_hidden()
        assert any(method=="PUT" and url.endswith("/user") for method,url,_ in requests)
        page.goto("http://127.0.0.1:8765/index.html")
        expect(page.locator("#ad-top")).to_be_hidden()
        expect(page.locator("#ad-secondary")).to_be_hidden()
        page.locator('a[href="about.html"]').click()
        expect(page.locator("h1")).to_have_text("About BargainIQ")
        assert not errors, errors
        browser.close()
    print("Browser smoke checks passed (mock feed, mobile viewport, navigation, calculator and signed-out account).")

if __name__=="__main__":
    main()
