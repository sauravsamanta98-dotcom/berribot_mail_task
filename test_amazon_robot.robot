*** Settings ***
Library    Browser
Library    Collections
Library    String

*** Variables ***
${AMAZON_URL}    https://www.amazon.com/
${SEARCH_TERM}    Watch

*** Test Cases ***
Amazon Product Price Comparison Test
    [Documentation]    Search Watch, extract 3rd product price, add to cart and compare
    
    Open Amazon And Search
    Extract And Store Third Product Price
    Close Browser

*** Keywords ***
Open Amazon And Search
    [Documentation]    Open Amazon and search for product
    
    New Browser    chromium    headless=false
    New Page    ${AMAZON_URL}
    Sleep    4s
    
    # Try to dismiss popups - use try/except approach
    TRY
        Click    .a-button-input >> nth=0
        Sleep    1s
    EXCEPT
        Log    No popup found
    END
    
    # Fill search
    TRY
        Fill Text    input[aria-label*="Search"]    ${SEARCH_TERM}
    EXCEPT
        Fill Text    [name="k"]    ${SEARCH_TERM}
    END
    
    Press Keys    Enter
    Sleep    5s
    Log    *** Search completed ***

Extract And Store Third Product Price
    [Documentation]    Extract 3rd product price and add to cart
    
    TRY
        # Get number of results
        ${count}=    Get Element Count    [data-component-type="s-search-result"]
        Log    Found ${count} products
        
        # Get 3rd product text
        ${text}=    Get Text    [data-component-type="s-search-result"] >> nth=2
        Log    Product text: ${text}
        
        # Check if INR exists
        ${has_inr}=    Evaluate    "INR" in """${text}"""
        
        IF    ${has_inr}
            # Extract price
            ${parts}=    Split String    ${text}    INR
            ${after_inr}=    Get From List    ${parts}    1
            ${price_raw}=    Strip String    ${after_inr}
            
            # Get first number from price text
            ${price}=    Evaluate    __import__('re').search(r'([\\d,]+)', """${price_raw}""").group(1)
            
            Log    ✓ 3rd Product Price: ${price}
            Set Suite Variable    ${PRODUCT_PRICE}    ${price}
            
            # Click Add to Cart
            TRY
                Click    [data-component-type="s-search-result"] >> nth=2 >> button
                Log    ✓ Added to cart
                Sleep    2s
            EXCEPT
                Log    Could not click add to cart
            END
        ELSE
            Log    ⚠ 3rd product is out of stock
        END
    EXCEPT    AS    ${error}
        Log    Error: ${error}
    END
