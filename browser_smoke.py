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
        retail=dict(name="Test lamp",retailer="Retailer A",url="https://example.invalid/lamp",price=100,shipping=20,condition="new",observed_at=now.isoformat(),currency="AUD",category="Lighting",brand="Example",mpn="L1",image_url="")
        retail["width_cm"]=50
        retail["depth_cm"]=30
        retail["price_history"]={"observations":[{"at":(now-timedelta(days=7)).isoformat(),"price":150},{"at":now.isoformat(),"price":100}]}
        second=dict(retail,retailer="Retailer B",url="https://example.invalid/lamp-b",price=110,shipping=0,price_history=None,width_cm=60)
        third=dict(retail,name="Test chair",category="Furniture",url="https://example.invalid/chair",shipping=None,price=90,price_history=None,width_cm=None,depth_cm=None)
        page.route("**/retail.json",lambda route:route.fulfill(json=dict(products=[retail,second,third],matches=[[retail,second]])))
        page.goto("http://127.0.0.1:8765/index.html")
        expect(page.locator("#retailResults")).to_contain_text("Test lamp")
        expect(page.locator("#retailResults .dropBadge")).to_contain_text("Down $50.00")
        page.locator("#retailResults .priceHistory summary").click()
        expect(page.locator("#retailResults .priceHistory svg")).to_be_visible()
        page.locator(".specFilters summary").click()
        page.locator("#specMaxWidth").fill("55")
        page.locator("#specMaxWidth").press("Tab")
        expect(page.locator("#retailResults article")).to_have_count(1)
        expect(page.locator("#retailResults article")).to_contain_text("Retailer A")
        page.locator("#specReset").click()
        page.locator("#specBudget").fill("115")
        page.locator("#specBasis").select_option("delivered")
        expect(page.locator("#retailResults article")).to_have_count(1)
        expect(page.locator("#retailResults article")).to_contain_text("Retailer B")
        page.locator("#specReset").click()
        page.locator("#smartQuery").fill("Find me a Test lamp under $115, max width 65 cm, including delivery")
        page.locator("#parseRequest").click()
        expect(page.locator("#specBudget")).to_have_value("115")
        expect(page.locator("#specMaxWidth")).to_have_value("65")
        expect(page.locator("#specBasis")).to_have_value("delivered")
        expect(page.locator("#search")).to_have_value("Test lamp")
        expect(page.locator("#retailResults article")).to_have_count(1)
        page.locator("#specReset").click()
        page.locator("#search").clear()
        page.locator("#specMaxWidth").fill("55")
        page.locator("#requestName").fill("My narrow lamp")
        page.locator("#saveRequest").click()
        expect(page.locator("#savedRequests")).to_contain_text("My narrow lamp")
        page.reload()
        expect(page.locator("#retailResults")).to_contain_text("Test lamp")
        page.locator(".specFilters summary").click()
        page.locator("#savedRequests button").filter(has_text="Run search").click()
        expect(page.locator("#specMaxWidth")).to_have_value("55")
        expect(page.locator("#retailResults article")).to_have_count(1)
        page.locator("#savedRequests button").filter(has_text="Remove").click()
        expect(page.locator("#savedRequests")).to_be_empty()
        page.locator("#specReset").click()
        page.locator(".specFilters summary").click()
        page.locator("#retailCategory").select_option("Lighting")
        expect(page.locator("#retailResults article")).to_have_count(2)
        page.locator("#retailSort").select_option("delivered")
        expect(page.locator("#retailResults article").first).to_contain_text("Retailer B")
        page.locator("#retailCategory").select_option("")
        expect(page.locator("#retailResults")).to_contain_text("Delivery not supplied")
        page.evaluate("window.recordRecent({title:'Test lamp',retailer:'Retailer A',url:'https://example.invalid/lamp'})")
        expect(page.locator("#recentGrid")).to_contain_text("Test lamp")
        page.locator("#clearRecent").click()
        expect(page.locator("#recentPanel")).to_be_hidden()
        expect(page.locator("#publicGrid")).to_contain_text("Browser test chair")
        expect(page.locator("#publicGrid")).not_to_contain_text("Expired test item")
        expect(page.locator("#showExamples")).not_to_be_checked()
        expect(page.locator("[data-feature=same]")).to_contain_text("Compare")
        expect(page.locator("[data-feature=clearance]")).to_contain_text("Clearance")
        page.locator("#heroQuery").fill("missing item")
        page.locator("#heroSearch button").click()
        expect(page.locator("#publicStatus")).to_contain_text("No matching")
        page.locator("#heroQuery").fill("")
        page.locator("#heroSearch button").click()
        expect(page.locator("#publicGrid article")).to_have_count(1)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
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
        expect(page.locator("#viewTitle")).to_have_text("Cars")
        assert "view=car" in page.url
        page.locator(".siteNav a").filter(has_text="Resell").click()
        expect(page.locator("#viewTitle")).to_have_text("Resell")
        expect(page.locator("#productCalc")).to_be_visible()
        page.locator("#buy").fill("100")
        page.locator("#sell").fill("150")
        page.locator("#fee").fill("10")
        page.locator("#cost").fill("5")
        expect(page.locator("#result")).to_contain_text("30")
        page.goto("http://127.0.0.1:8765/index.html?view=same")
        expect(page.locator("#viewTitle")).to_have_text("Compare")
        expect(page.locator("#retailPanel")).to_be_visible()
        expect(page.locator(".compareTable")).to_contain_text("Retailer A")
        expect(page.locator(".compareTable")).to_contain_text("$120.00")
        expect(page.locator(".compareTable")).to_contain_text("$110.00")
        page.goto("http://127.0.0.1:8765/index.html?deal=test-only")
        expect(page.locator("#offer-test-only")).to_be_visible()
        page.goto("http://127.0.0.1:8765/index.html?deal=expired")
        expect(page.locator("#publicStatus")).to_contain_text("unavailable or has expired")
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
        # Signed-in account flows with synthetic API data only.
        uid="11111111-1111-4111-8111-111111111111"
        deal_id="22222222-2222-4222-8222-222222222222"
        verified=dict(offer,id=deal_id)
        saved=[]
        targets=[]
        account_searches=[]
        headers={"access-control-allow-origin":"*","access-control-allow-methods":"GET,POST,DELETE,OPTIONS","access-control-allow-headers":"apikey,authorization,content-type,prefer"}
        def mock_account(route):
            request=route.request
            if request.method=="OPTIONS":
                route.fulfill(status=204,headers=headers)
                return
            url=request.url
            if "/auth/v1/token" in url:
                result={"access_token":"test-token","user":{"id":uid}}
            elif "/public_deals?" in url:
                result=[verified]
            elif "/watchlists" in url:
                if request.method=="POST":
                    saved.append(dict(request.post_data_json,id="test-watch"))
                result=saved
            elif "/saved_searches" in url:
                if request.method=="POST":
                    account_searches.append(dict(request.post_data_json,id="test-search"))
                elif request.method=="DELETE":
                    account_searches.clear()
                result=account_searches
            elif "/price_alerts" in url:
                if request.method=="POST":
                    targets.append(dict(request.post_data_json,id="test-target"))
                result=targets
            else:
                result=[]
            route.fulfill(json=result,headers=headers)
        page.route("**/auth/v1/token?*",mock_account)
        page.route("**/rest/v1/**",mock_account)
        page.goto("http://127.0.0.1:8765/account.html?save="+deal_id)
        page.locator("#auth [name=email]").fill("test@example.invalid")
        page.locator("#auth [name=password]").fill("Test-password-123")
        page.locator("#auth button[value=login]").click()
        expect(page.locator("#pendingSaveTitle")).to_contain_text("Browser test chair")
        page.locator("#confirmSave").click()
        expect(page.locator("#items")).to_contain_text("Browser test chair")
        expect(page.locator("#items")).to_contain_text("$99.95")
        page.locator("#items button").filter(has_text="Set price target").click()
        expect(page.locator("#alertsPanel")).to_be_visible()
        page.locator("#targetForm [name=target_price]").fill("100")
        page.locator("#targetForm button").click()
        expect(page.locator("#targetItems")).to_contain_text("Target reached")
        assert len(saved)==1 and len(targets)==1
        page.evaluate("""localStorage.setItem('bargainiq-saved-searches-v1',JSON.stringify([{name:'Account lamp',fields:{search:'Test lamp',specBudget:'115',specBasis:'delivered',retailCategory:'Lighting'},clearance:false}]))""")
        page.locator('[data-view="searchPanel"]').click()
        expect(page.locator("#accountSearches")).to_contain_text("No account shopping requests")
        page.locator("#syncSearches").click()
        expect(page.locator("#accountSearches")).to_contain_text("Account lamp")
        assert len(account_searches)==1
        page.locator("#syncSearches").click()
        expect(page.locator("#status")).to_contain_text("0 shopping requests imported")
        href=page.locator("#accountSearches a").get_attribute("href")
        second_device=browser.new_page(viewport={"width":390,"height":844})
        second_device.route("**/rest/v1/public_deals?*",lambda route:route.fulfill(json=[offer,expired],headers={"access-control-allow-origin":"*"}))
        second_device.route("**/retail.json",lambda route:route.fulfill(json=dict(products=[retail,second,third],matches=[[retail,second]])))
        second_device.goto("http://127.0.0.1:8765/"+href)
        expect(second_device.locator("#specBudget")).to_have_value("115")
        expect(second_device.locator("#retailCategory")).to_have_value("Lighting")
        expect(second_device.locator("#retailResults article")).to_have_count(1)
        expect(second_device.locator("#retailResults article")).to_contain_text("Retailer B")
        assert "#shopping=" not in second_device.url
        second_device.close()
        page.locator("#accountSearches button").filter(has_text="Remove").click()
        expect(page.locator("#accountSearches")).to_contain_text("No account shopping requests")
        assert not account_searches
        page.unroute("**/rest/v1/**",mock_account)
        page.unroute("**/auth/v1/token?*",mock_account)
        page.goto("http://127.0.0.1:8765/index.html")
        expect(page.locator("#ad-top")).to_be_hidden()
        expect(page.locator("#ad-secondary")).to_be_hidden()
        page.locator('a[href="about.html"]').click()
        expect(page.locator("h1")).to_have_text("About BargainIQ")
        page.evaluate("""localStorage.setItem("bargainiq-watch","[]");localStorage.setItem("bargainiq-saved-searches-v1","[]");localStorage.setItem("bargainiq-recent-v1","[]");localStorage.setItem("bargainiq-submission","{}");localStorage.setItem("unrelated-test-key","keep")""")
        page.once("dialog", lambda dialog: dialog.dismiss())
        page.locator("#clearLocal").click()
        assert page.evaluate("localStorage.getItem('bargainiq-watch')") == "[]"
        page.once("dialog", lambda dialog: dialog.accept())
        page.locator("#clearLocal").click()
        expect(page.locator("#privacyStatus")).to_contain_text("Account records were not changed")
        assert page.evaluate("""['bargainiq-watch','bargainiq-saved-searches-v1','bargainiq-recent-v1','bargainiq-submission'].every(k=>localStorage.getItem(k)===null)""")
        assert page.evaluate("localStorage.getItem('unrelated-test-key')") == "keep"
        assert not errors, errors
        browser.close()
    print("Browser smoke checks passed (mock feed, mobile viewport, navigation, calculator and signed-out account).")

if __name__=="__main__":
    main()
