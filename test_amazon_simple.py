from playwright.sync_api import Page
import pytest
import time
import re


def test_amazon_watch_price(page: Page):
    """
    Simple test to search for watch on Amazon and extract its price
    """
    # Navigate to Amazon
    page.goto("https://www.amazon.com/")
    time.sleep(3)
    
    # Close any popups
    try:
        page.locator(".a-button-input").first.click(timeout=3000)
    except:
        pass
    
    # Search for Watch
    search_box = page.get_by_role("searchbox", name="Search Amazon")
    search_box.fill("Watch")
    page.keyboard.press("Enter")
    page.wait_for_load_state("load")
    time.sleep(2)
    
    print("*** Search completed ***")
    
    # Wait for products to load
    page.wait_for_selector("[data-component-type='s-search-result']", timeout=10000)
    time.sleep(2)
    
    # Get the 3rd product
    results = page.locator("[data-component-type='s-search-result']")
    total_products = results.count()
    print(f"Total products found: {total_products}")
    
    if total_products < 3:
        raise AssertionError(f"Expected at least 3 products, but found {total_products}")
    
    # Extract price from 3rd product
    third_product_text = results.nth(2).text_content()
    
    # Strip all whitespace and clean the product text
    third_product_text = ' '.join(third_product_text.split())
    print(f"\nFull product text (stripped):\n{third_product_text}\n")
    
    # Check if INR exists in the text
    if "INR" in third_product_text:
        # Extract everything after INR
        price = extract_price(third_product_text)
        if price:
            print(f"✓ 3rd Product Price: {price}")
            
            # Store price in variable
            third_product_price = price
            print(f"Price stored in variable: {third_product_price}")
            
            # Click "Add to Cart" button for the 3rd product
            try:
                # Try to find and click the "Add to Cart" button within the 3rd product
                add_to_cart_btn = results.nth(2).locator("button:has-text('Add to cart')")
                add_to_cart_btn.click(timeout=5000)
                print("✓ Added to cart successfully!")
                time.sleep(2)
            except Exception as e:
                print(f"⚠ Could not click Add to Cart button: {str(e)}")
                print("Trying alternative selectors...")
                try:
                    # Alternative: Look for button with aria-label
                    add_to_cart_btn = results.nth(2).locator("button[aria-label*='Add to cart']")
                    add_to_cart_btn.click(timeout=5000)
                    print("✓ Added to cart successfully!")
                    time.sleep(2)
                except:
                    print("⚠ Failed to add to cart")
                    return
            
            # Navigate to cart by clicking cart icon
            try:
                page.locator(".nav-cart-icon").click(timeout=5000)
                time.sleep(3)
                print("✓ Navigated to cart")
            except:
                print("⚠ Failed to navigate to cart")
                return
            
            # Extract cart total price
            try:
                cart_price_locator = page.locator("[data-a-color='price']").first
                cart_price_text = cart_price_locator.text_content()
                print(f"Cart price text: {cart_price_text}")
                
                # Extract INR value from cart
                cart_total = extract_price(cart_price_text)
                print(f"Cart total: {cart_total}")
                
                # Compare prices
                print(f"\n{'='*50}")
                print(f"3rd Product Price: {third_product_price}")
                print(f"Cart Total Price: {cart_total}")
                
                if third_product_price == cart_total:
                    print(f"✓ PRICES MATCH! Both are {third_product_price}")
                else:
                    print(f"❌ PRICE MISMATCH! Product: {third_product_price} vs Cart: {cart_total}")
                print(f"{'='*50}\n")
            except Exception as e:
                print(f"⚠ Could not extract cart price: {str(e)}")
                return
        else:
            print("⚠ 3rd product is out of stock")
    else:
        print("⚠ 3rd product is out of stock")


def extract_price(text: str) -> str:
    """
    Extract price value after INR keyword
    """
    if not text or "INR" not in text:
        return None
    
    # Split by INR and get what comes after
    parts = text.split("INR")
    if len(parts) > 1:
        after_inr = parts[1].strip()
        
        # Extract numbers from the text after INR
        match = re.search(r'([\d,]+(?:\.?\d{1,2})?)', after_inr)
        if match:
            return match.group(1).strip() 
    return None
    return None
